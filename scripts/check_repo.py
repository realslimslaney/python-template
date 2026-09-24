"""Dependency-free checks for the repository scaffold and local documentation links."""

from __future__ import annotations

import json
import re
import sys
import tomllib
from pathlib import Path
from urllib.parse import unquote, urlsplit

from sync_agent_instructions import check as check_agent_instructions


def check(root: Path) -> list[str]:
    errors = []
    for section in ("tutorials", "how-to", "reference", "explanation"):
        if not list((root / "docs" / section).glob("*.md")):
            errors.append(f"docs/{section} needs at least one Markdown page.")
    documents = [*root.glob("*.md"), *root.glob("docs/**/*.md"), *root.glob("docs/**/*.qmd")]
    for document in documents:
        if "_site" in document.parts or ".quarto" in document.parts:
            continue
        text = document.read_text(encoding="utf-8")
        # Fenced examples are not document links.
        prose = re.sub(r"```[^\n]*\n[\s\S]*?```", "", text)
        for match in re.finditer(r"\]\(([^)]+)\)", prose):
            target = match.group(1).split(' "', 1)[0].strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            path = (document.parent / unquote(parsed.path)).resolve()
            if not path.exists():
                errors.append(f"{document.relative_to(root)}: missing link target {target}")
    for folder in (".github", ".claude", ".codex"):
        for path in (root / folder).rglob("*.json"):
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except (ValueError, OSError) as error:
                errors.append(f"{path.relative_to(root)}: {error}")
    for path in [*root.glob("*.toml"), *root.glob(".codex/agents/*.toml")]:
        try:
            tomllib.loads(path.read_text(encoding="utf-8"))
        except (ValueError, OSError) as error:
            errors.append(f"{path.relative_to(root)}: {error}")
    for role in ("committer", "pr-manager", "docs-maintainer"):
        skill = root / ".agents/skills" / role / "SKILL.md"
        canonical = f".agents/skills/{role}/SKILL.md"
        try:
            content = skill.read_text(encoding="utf-8")
            if not content.startswith("---\n") or f"\nname: {role}\n" not in content:
                errors.append(f"{canonical}: missing or mismatched skill frontmatter.")
            if not re.search(r"^description: .+", content, re.MULTILINE):
                errors.append(f"{canonical}: missing skill description.")
            codex = tomllib.loads((root / f".codex/agents/{role}.toml").read_text(encoding="utf-8"))
            if codex.get("name") != role.replace("-", "_") or not codex.get("description"):
                errors.append(f"{role}: invalid Codex identity.")
        except (OSError, ValueError) as error:
            errors.append(f"{role}: {error}")
    for path in (".codex/hooks.json", ".claude/settings.json"):
        try:
            config = json.loads((root / path).read_text(encoding="utf-8"))
            handlers = config["hooks"]["PreToolUse"][0]["hooks"]
            if not any("scripts/gate_commit.py" in handler["command"] for handler in handlers):
                errors.append(f"{path}: missing shared commit gate.")
        except (OSError, ValueError, KeyError, IndexError, TypeError) as error:
            errors.append(f"{path}: {error}")
    errors.extend(check_agent_instructions(root))
    return errors


if __name__ == "__main__":
    findings = check(Path(__file__).resolve().parents[1])
    if findings:
        print("\n".join(findings), file=sys.stderr)
        raise SystemExit(1)
    print("Repository configuration and documentation links passed.")
