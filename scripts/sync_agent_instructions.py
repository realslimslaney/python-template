"""Materialize complete client instructions from the shared project policy and skills."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROLES = ("committer", "pr-manager", "docs-maintainer")


def outputs(root: Path) -> dict[Path, str]:
    """Return the managed client files without modifying the repository."""
    result = {Path("CLAUDE.md"): (root / "AGENTS.md").read_text(encoding="utf-8")}
    for role in ROLES:
        path = Path(".agents/skills") / role / "SKILL.md"
        skill = (root / path).read_text(encoding="utf-8")
        match = re.fullmatch(r"---\n(.*?)\n---\n(.*)", skill, re.DOTALL)
        if not match:
            raise ValueError(f"{path}: expected YAML frontmatter and a skill body.")
        header, body = match.groups()
        # The built-in skills deliberately use only unquoted name/description scalars.
        fields = dict(line.split(": ", 1) for line in header.splitlines() if ": " in line)
        if fields.get("name") != role or not fields.get("description") or not body.strip():
            raise ValueError(f"{path}: expected matching name, description, and nonempty body.")
        if set(fields) != {"name", "description"}:
            raise ValueError(f"{path}: extend this generator before adding frontmatter fields.")
        description = fields["description"]
        body = body.strip() + "\n"
        result[Path(".claude/skills") / role / "SKILL.md"] = skill
        result[Path(".claude/agents") / f"{role}.md"] = (
            f"---\nname: {role}\ndescription: {description}\n---\n\n{body}"
        )
        escaped_body = body.replace("\\", "\\\\").replace('"', '\\"')
        result[Path(".codex/agents") / f"{role}.toml"] = (
            f"name = {json.dumps(role.replace('-', '_'))}\n"
            f"description = {json.dumps(description)}\n"
            f'developer_instructions = """\n{escaped_body}"""\n'
        )
    return result


def check(root: Path) -> list[str]:
    """Report missing or stale managed files without repairing them."""
    try:
        expected = outputs(root)
    except (OSError, ValueError) as error:
        return [f"Agent sources: {error}"]
    errors = []
    for relative, content in expected.items():
        path = root / relative
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            errors.append(f"{relative.as_posix()}: missing or stale; run just agents-sync.")
    return errors


def sync(root: Path) -> None:
    for relative, content in outputs(root).items():
        path = root / relative
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Report drift without writing files.")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.check:
        errors = check(root)
        print("\n".join(errors) if errors else "Agent instructions and skills are synchronized.")
        return int(bool(errors))
    sync(root)
    print("Updated complete Claude and Codex instructions from shared sources.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
