# Configuration reference

- `AGENTS.md`: shared contributor-agent policy.
- `.agents/skills/`: canonical committer, PR manager, and docs maintainer procedures.
- `.claude/agents/` and `.codex/agents/`: client adapters; no fixed model or permission mode.
- `.claude/settings.json` and `.codex/hooks.json`: PreToolUse commit gate wiring.
- `.github/repository-policy.json`: fallback default branch, version policy, check command,
  and the 240-second internal check timeout. Remote default-branch metadata takes precedence.
- `docs/_quarto.yml`: Quarto website, navigation, themes, and render patterns.
- `.github/workflows/ci.yml`: Windows and Ubuntu checks on pushes and pull requests.

Repository tooling uses only Python's standard library. It checks local Markdown links,
required Diataxis directories, agent adapters, JSON/TOML parsing, and hook configuration.
External URLs are not fetched during checks. Tests use temporary repositories and synthetic data.

The Python template keeps metadata, build configuration, pytest, and Ruff settings in
`pyproject.toml`; `uv.lock` records dependency resolutions. The bare-bones template uses
`version.txt` and release-please's configuration and manifest for releases.
