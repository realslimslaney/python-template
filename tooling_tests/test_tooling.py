"""Behavioral tests for commit safety, staged versions, and documentation validation."""

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


gate = module("gate_commit", ROOT / "scripts/gate_commit.py")
checker = module("check_repo", ROOT / "scripts/check_repo.py")


class CommandTests(unittest.TestCase):
    def test_noncommit(self):
        self.assertIsNone(gate.commit_target("git status --short", ROOT))

    def test_quotes_and_target(self):
        target = ROOT / "directory with spaces"
        self.assertEqual(
            gate.commit_target(f'git -C "{target}" commit -m "fix: semicolon; is prose"', ROOT), target
        )

    def test_rejected_forms(self):
        for command in [
            'git commit --no-verify -m "fix: bypass"',
            'git commit -n -m "fix: bypass"',
            'git commit -am "fix: auto stage"',
            'git commit file.py -m "fix: partial"',
            'git -c core.hooksPath=x commit -m "fix: override"',
            'git add .; git commit -m "fix: combined"',
            'cd elsewhere && git commit -m "fix: target"',
            'git commit -m "$MESSAGE"',
            'git commit -m "unclosed',
        ]:
            with self.subTest(command=command), self.assertRaises(gate.Denied):
                gate.commit_target(command, ROOT)

    def test_malformed_payload_denies(self):
        for payload in (None, {}, {"tool_input": "oops"}, {"tool_input": {"command": 3}}):
            with self.subTest(payload=payload), self.assertRaises(gate.Denied):
                gate.check_payload(payload)

    def test_actual_hook_protocol(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/gate_commit.py")],
            input="{broken",
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        decision = json.loads(result.stdout)["hookSpecificOutput"]
        self.assertEqual(decision["permissionDecision"], "deny")
        self.assertIn("BLOCKED", decision["permissionDecisionReason"])


class RepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="hook-test with spaces-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Template Test")
        self.git("config", "user.email", "test@example.invalid")
        self.policy = {
            "default_branch": "main",
            "version_policy": "manual-python",
            "check_command": [sys.executable, "check.py"],
            "check_timeout_seconds": 5,
        }
        (self.root / ".github").mkdir()
        (self.root / ".github/repository-policy.json").write_text(json.dumps(self.policy), encoding="utf-8")
        self.project("0.1.0")
        self.lock()
        (self.root / "check.py").write_text("raise SystemExit(0)\n", encoding="utf-8")
        self.git("add", ".github/repository-policy.json", "pyproject.toml", "uv.lock", "check.py")

    def git(self, *args):
        return subprocess.run(
            ["git", "-C", str(self.root), *args], check=True, capture_output=True, text=True
        )

    def project(self, version, dependencies="[]"):
        (self.root / "pyproject.toml").write_text(
            f'[project]\nname = "example"\nversion = "{version}"\ndependencies = {dependencies}\n',
            encoding="utf-8",
        )

    def lock(self, version="0.1.0", dependency_version="1.0.0"):
        (self.root / "uv.lock").write_text(
            f'[[package]]\nname = "example"\nversion = "{version}"\nsource = {{ editable = "." }}\n'
            f'[[package]]\nname = "dependency"\nversion = "{dependency_version}"\n',
            encoding="utf-8",
        )

    def baseline(self):
        self.git("commit", "-m", "chore: fixture")
        self.git("switch", "-c", "feat/example")

    def payload(self, directory=None):
        return {
            "cwd": str(directory or self.root),
            "tool_input": {"command": 'git commit -m "feat: example"'},
        }

    def test_configured_hook_launchers_preserve_denial(self):
        scripts = self.root / "scripts"
        scripts.mkdir()
        (scripts / "gate_commit.py").write_text(
            (ROOT / "scripts/gate_commit.py").read_text(encoding="utf-8"), encoding="utf-8"
        )
        nested = self.root / "nested"
        nested.mkdir()
        config = json.loads((ROOT / ".codex/hooks.json").read_text(encoding="utf-8"))
        handler = config["hooks"]["PreToolUse"][0]["hooks"][0]
        import os

        command = handler["commandWindows"] if os.name == "nt" else handler["command"]
        result = subprocess.run(
            command,
            shell=True,
            cwd=nested,
            input=json.dumps(self.payload(nested)),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"], "deny")
        if os.name == "nt":
            result = subprocess.run(
                ["powershell.exe", "-NoProfile", "-Command", command],
                cwd=nested,
                input=json.dumps(self.payload(nested)),
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_unborn_default_branch_denies(self):
        with self.assertRaisesRegex(gate.Denied, "feature branch"):
            gate.check_payload(self.payload())

    def test_first_feature_commit_passes(self):
        self.git("switch", "-c", "chore/bootstrap")
        gate.check_payload(self.payload())

    def test_existing_default_and_detached_deny(self):
        self.git("commit", "-m", "chore: fixture")
        with self.assertRaisesRegex(gate.Denied, "feature branch"):
            gate.check_payload(self.payload())
        self.git("checkout", "--detach")
        with self.assertRaisesRegex(gate.Denied, "feature branch"):
            gate.check_payload(self.payload())

    def test_remote_default_takes_precedence(self):
        self.baseline()
        self.git("update-ref", "refs/remotes/origin/feat/example", "HEAD")
        self.git("symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/feat/example")
        with self.assertRaisesRegex(gate.Denied, "feature branch"):
            gate.check_payload(self.payload())

    def test_subdirectory_and_cmd_workdir(self):
        self.baseline()
        directory = self.root / "nested directory"
        directory.mkdir()
        gate.check_payload(self.payload(directory))
        gate.check_payload(
            {"cwd": str(ROOT), "tool_input": {"cmd": "git commit --dry-run", "workdir": str(directory)}}
        )

    def test_dependency_change_without_bump_denies(self):
        self.baseline()
        self.project("0.1.0", '["dependency>=2"]')
        self.git("add", "pyproject.toml")
        with self.assertRaisesRegex(gate.Denied, "version increase"):
            gate.check_payload(self.payload())

    def test_lock_only_dependency_update_denies(self):
        self.baseline()
        self.lock(dependency_version="2.0.0")
        self.git("add", "uv.lock")
        with self.assertRaisesRegex(gate.Denied, "version increase"):
            gate.check_payload(self.payload())

    def test_dependency_change_with_bump_passes(self):
        self.baseline()
        self.project("0.2.0", '["dependency>=2"]')
        self.lock("0.2.0", "2.0.0")
        self.git("add", "pyproject.toml", "uv.lock")
        gate.check_payload(self.payload())

    def test_unstaged_bump_does_not_count(self):
        self.baseline()
        self.lock(dependency_version="2.0.0")
        self.git("add", "uv.lock")
        self.project("0.2.0")
        with self.assertRaisesRegex(gate.Denied, "version increase"):
            gate.check_payload(self.payload())

    def test_formatting_and_root_version_are_not_dependencies(self):
        self.baseline()
        with (self.root / "uv.lock").open("a", encoding="utf-8") as stream:
            stream.write("\n# Formatting only\n")
        self.git("add", "uv.lock")
        gate.check_payload(self.payload())
        self.project("0.1.1")
        self.lock("0.1.1")
        self.git("add", "pyproject.toml", "uv.lock")
        gate.check_payload(self.payload())

    def test_unstaged_fix_cannot_hide_broken_index(self):
        self.baseline()
        (self.root / "check.py").write_text("raise SystemExit(1)\n", encoding="utf-8")
        self.git("add", "check.py")
        (self.root / "check.py").write_text("raise SystemExit(0)\n", encoding="utf-8")
        with self.assertRaisesRegex(gate.Denied, "Staged checks failed"):
            gate.check_payload(self.payload())
        self.assertEqual((self.root / "check.py").read_text(), "raise SystemExit(0)\n")

    def test_missing_tool_denies(self):
        self.policy["check_command"] = ["no-such-template-check-tool"]
        with self.assertRaisesRegex(gate.Denied, "missing from PATH"):
            gate.check_snapshot(self.root, self.policy)

    def test_timeout_denies(self):
        real_run = subprocess.run

        def run(command, **kwargs):
            if command[0] == "git":
                return real_run(command, **kwargs)
            raise subprocess.TimeoutExpired(command, 5)

        with patch.object(gate.subprocess, "run", side_effect=run):
            with self.assertRaisesRegex(gate.Denied, "timed out"):
                gate.check_snapshot(self.root, self.policy)

    def test_manual_version_decrease_denies(self):
        self.baseline()
        self.project("0.0.9")
        self.git("add", "pyproject.toml")
        with self.assertRaisesRegex(gate.Denied, "decrease"):
            gate.check_payload(self.payload())

    def test_release_policy_does_not_require_python(self):
        self.policy["version_policy"] = "release-please"
        self.git("rm", "--cached", "pyproject.toml", "uv.lock")
        gate.check_version(self.root, self.policy)


class DocumentationTests(unittest.TestCase):
    def test_scaffold_is_valid(self):
        self.assertEqual(checker.check(ROOT), [])

    def test_broken_link_is_reported(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "README.md").write_text("[Missing](does-not-exist.md)\n", encoding="utf-8")
            self.assertTrue(any("does-not-exist.md" in item for item in checker.check(root)))


if __name__ == "__main__":
    unittest.main()
