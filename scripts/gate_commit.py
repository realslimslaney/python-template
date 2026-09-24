"""Shared PreToolUse commit gate. See docs/how-to/ai-tooling.md for its boundaries."""

from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path


class Denied(Exception):
    """A commit does not satisfy the repository policy."""


def run_git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    if check and result.returncode:
        raise Denied(result.stderr.strip() or "Git inspection failed.")
    return result


def is_commit_segment(raw: list[str]) -> bool:
    tokens = [token[1:-1] if token[:1] in ("'", '"') and token[-1:] == token[:1] else token for token in raw]
    if tokens[:1] in (["command"], ["sudo"]):
        tokens = tokens[1:]
    if not tokens or tokens[0].lower() not in ("git", "git.exe"):
        return False
    position = 1
    value_flags = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path", "--config-env"}
    while position < len(tokens) and tokens[position].startswith("-"):
        position += 2 if tokens[position] in value_flags else 1
    return position < len(tokens) and tokens[position] == "commit"


def commit_target(command: str, cwd: Path) -> Path | None:
    """Accept a small, unambiguous subset of standalone git commit commands."""
    if not re.search(r"\bgit(?:\.exe)?\b[\s\S]*?\bcommit\b", command, re.IGNORECASE):
        return None
    lexer = shlex.shlex(command, posix=False, punctuation_chars=";&|<>\n()")
    lexer.whitespace = " \t\r"
    lexer.whitespace_split = True
    lexer.commenters = ""
    try:
        raw = list(lexer)
    except ValueError as error:
        raise Denied(f"Cannot parse commit command: {error}") from error
    # Look at command verbs, not prose such as rg "git commit" or git log --grep commit.
    segments = [[]]
    for token in raw:
        if token and all(char in ";&|<>\n()" for char in token):
            segments.append([])
        else:
            segments[-1].append(token)
    if not any(is_commit_segment(segment) for segment in segments):
        return None
    if any(token and all(char in ";&|<>\n()" for char in token) for token in raw):
        raise Denied("Run git commit alone; do staging and directory changes in separate calls.")
    if any("$" in token or "`" in token for token in raw):
        raise Denied("Use literal commit arguments; shell expansion cannot be validated.")
    tokens = [token[1:-1] if token[:1] in ("'", '"') and token[-1:] == token[:1] else token for token in raw]
    if not tokens or tokens[0].lower() not in ("git", "git.exe"):
        raise Denied("Use a standalone git commit with the shell tool's working directory set.")
    index = 1
    target = cwd
    while index < len(tokens) and tokens[index] == "-C":
        if index + 1 >= len(tokens):
            raise Denied("git -C requires a directory.")
        target = (target / tokens[index + 1]).resolve()
        index += 2
    if index >= len(tokens) or tokens[index] != "commit":
        raise Denied("Git configuration overrides and wrappers are not supported for commits.")
    args = tokens[index + 1 :]
    position = 0
    value_flags = {"-m", "--message", "-F", "--file"}
    flag_only = {
        "--allow-empty",
        "--allow-empty-message",
        "--dry-run",
        "--quiet",
        "-q",
        "--verbose",
        "-v",
        "--signoff",
        "-s",
    }
    while position < len(args):
        arg = args[position]
        if arg in ("--no-verify", "-n"):
            raise Denied("Verification bypasses are not permitted.")
        if arg in value_flags:
            if position + 1 >= len(args):
                raise Denied(f"{arg} requires a value.")
            position += 2
        elif any(arg.startswith(flag + "=") for flag in ("--message", "--file")):
            position += 1
        elif arg in flag_only:
            position += 1
        else:
            raise Denied(
                f"Unsupported commit argument {arg!r}; stage explicit paths first, then use -m or -F."
            )
    return target


def dependency_signature(project: dict, lock: dict) -> str:
    metadata = project.get("project", {})
    uv = project.get("tool", {}).get("uv", {})
    packages = []
    for original in lock.get("package", []):
        package = dict(original)
        source = package.get("source", {})
        if source.get("editable") == "." or source.get("virtual") == ".":
            # The root version changes as a consequence of a bump, not a dependency update.
            package.pop("version", None)
        packages.append(package)
    value = {
        "dependencies": sorted(metadata.get("dependencies", [])),
        "optional": metadata.get("optional-dependencies", {}),
        "groups": project.get("dependency-groups", {}),
        "build": project.get("build-system", {}),
        "sources": uv.get("sources", {}),
        "overrides": uv.get("override-dependencies", []),
        "constraints": uv.get("constraint-dependencies", []),
        "packages": sorted(packages, key=lambda item: json.dumps(item, sort_keys=True)),
    }
    return json.dumps(value, sort_keys=True)


def version_tuple(project: dict) -> tuple[int, int, int]:
    value = project.get("project", {}).get("version", "")
    if not re.fullmatch(r"\d+\.\d+\.\d+", value):
        raise Denied("The manual policy requires a numeric major.minor.patch project version.")
    return tuple(int(part) for part in value.split("."))


def read_index_toml(root: Path, revision: str, path: str) -> dict:
    result = run_git(root, "show", f"{revision}:{path}", check=False)
    if result.returncode:
        return {}
    return tomllib.loads(result.stdout)


def check_version(root: Path, policy: dict) -> None:
    if policy["version_policy"] != "manual-python":
        return
    staged = read_index_toml(root, "", "pyproject.toml")
    staged_lock = read_index_toml(root, "", "uv.lock")
    if not staged or not staged_lock:
        raise Denied("Stage both pyproject.toml and uv.lock for the Python project.")
    new_version = version_tuple(staged)
    previous = read_index_toml(root, "HEAD", "pyproject.toml")
    if not previous:
        return  # First commit establishes the version.
    old_version = version_tuple(previous)
    if new_version < old_version:
        raise Denied("Project versions must not decrease.")
    previous_lock = read_index_toml(root, "HEAD", "uv.lock")
    if dependency_signature(previous, previous_lock) != dependency_signature(staged, staged_lock):
        if new_version <= old_version:
            raise Denied(
                "Dependency changes require a version increase in staged pyproject.toml and uv.lock."
            )


def check_snapshot(root: Path, policy: dict) -> None:
    command = policy["check_command"]
    if not isinstance(command, list) or not command or not all(isinstance(item, str) for item in command):
        raise Denied("check_command must be a nonempty argument list.")
    executable = shutil.which(command[0])
    if executable is None:
        raise Denied(f"Required check tool {command[0]!r} is missing from PATH.")
    timeout = policy["check_timeout_seconds"]
    if not isinstance(timeout, int) or not 1 <= timeout <= 240:
        raise Denied("The internal check timeout must be between 1 and 240 seconds.")
    with tempfile.TemporaryDirectory(prefix="staged-check-") as temporary:
        snapshot = Path(temporary)
        run_git(root, "checkout-index", "--all", "--prefix=" + snapshot.as_posix() + "/")
        environment = os.environ.copy()
        # uv must choose the snapshot's own environment, not the parent checkout's.
        for key in ("VIRTUAL_ENV", "UV_PROJECT_ENVIRONMENT", "UV_PROJECT", "UV_WORKING_DIRECTORY"):
            environment.pop(key, None)
        try:
            result = subprocess.run(
                [executable, *command[1:]],
                cwd=snapshot,
                env=environment,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as error:
            raise Denied("Staged checks timed out. Investigate before committing.") from error
        if result.returncode:
            tail = "\n".join((result.stdout + "\n" + result.stderr).splitlines()[-35:])
            raise Denied("Staged checks failed:\n" + tail)


def check_payload(payload: dict) -> None:
    if not isinstance(payload, dict):
        raise Denied("Expected a JSON object.")
    tool_input = payload.get("tool_input", {})
    if not isinstance(tool_input, dict):
        raise Denied("Expected an object for tool_input.")
    command = tool_input.get("command", tool_input.get("cmd"))
    if not isinstance(command, str):
        raise Denied("Expected a shell command in tool_input.command or tool_input.cmd.")
    cwd = Path(tool_input.get("workdir") or tool_input.get("cwd") or payload.get("cwd") or os.getcwd())
    target = commit_target(command, cwd)
    if target is None:
        return
    if any(os.environ.get(key) for key in ("GIT_INDEX_FILE", "GIT_DIR", "GIT_WORK_TREE")):
        raise Denied("Custom Git index/work-tree environment variables are not supported for commits.")
    root = Path(run_git(target, "rev-parse", "--show-toplevel").stdout.strip())
    policy = json.loads((root / ".github/repository-policy.json").read_text(encoding="utf-8"))
    branch = run_git(root, "symbolic-ref", "--short", "-q", "HEAD", check=False).stdout.strip()
    remote_default = run_git(
        root, "symbolic-ref", "--short", "-q", "refs/remotes/origin/HEAD", check=False
    ).stdout.strip()
    default = remote_default.removeprefix("origin/") or policy["default_branch"]
    if not branch or branch == default:
        raise Denied("Commit on a focused feature branch, never the default branch or detached HEAD.")
    run_git(root, "diff", "--cached", "--check")
    check_version(root, policy)
    check_snapshot(root, policy)


def main() -> int:
    try:
        check_payload(json.load(sys.stdin))
    except (Denied, OSError, ValueError, KeyError, TypeError) as error:
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": f"BLOCKED: {error}",
                    }
                }
            )
        )
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
