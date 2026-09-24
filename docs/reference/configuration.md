# Configuration reference

- `AGENTS.md`: shared project policy and Codex instruction entrypoint.
- `CLAUDE.md`: complete generated project policy for Claude.
- `.agents/skills/`: canonical committer, PR manager, and docs maintainer procedures.
- `.claude/skills/`: complete generated Claude skills.
- `.claude/agents/` and `.codex/agents/`: complete generated native role definitions;
  no fixed model or permission mode.
- `scripts/sync_agent_instructions.py`: synchronize the root Claude policy and the
  three built-in workflows; `--check` detects drift without writing.
- `.claude/settings.json` and `.codex/hooks.json`: PreToolUse commit gate wiring.
- `.github/repository-policy.json`: fallback default branch, version policy, check command,
  and the 240-second internal check timeout. Remote default-branch metadata takes precedence.
- `docs/_quarto.yml`: Quarto website, navigation, themes, and render patterns.
- `.github/workflows/ci.yml`: Windows and Ubuntu checks on pushes and pull requests.

Repository tooling uses only Python's standard library. It checks local Markdown links,
required Diataxis directories, complete synchronized agent files, JSON/TOML parsing, and hook configuration.
External URLs are not fetched during checks. Tests use temporary repositories and synthetic data.

The Python template keeps metadata, build configuration, pytest, and Ruff settings in
`pyproject.toml`; `uv.lock` records dependency resolutions. The general template uses
`version.txt` and release-please's configuration and manifest for releases.
