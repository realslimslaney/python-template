# Agent instructions

This is the shared policy for Claude, Codex, and other coding agents.

## Working practices

- Read README and the affected documentation before changing behavior.
- Keep changes focused. Preserve unrelated edits and use synthetic test data.
- Run `just check` before finishing. Report failures and limitations accurately.
- Write clear, concise US English; avoid em-dashes and opaque abbreviations.
- Never commit credentials, real private data, or local machine configuration.

## Git workflow

- Commit only after explicit user authorization. Existing authorization persists;
  do not ask again when the user has already authorized the intended commit or publication.
- Delegate authorized commits to `committer`, quoting the user's authorization verbatim.
  Use the matching skill directly only when the client cannot run custom agents.
- Work on a feature branch, never the default branch. Stage explicit paths only.
- Never bypass hooks, force-push, amend published commits, or merge without authorization.
- Run `docs-maintainer` before preparing a PR, then `pr-manager` for an already-pushed branch.
- Committer owns commits and authorized pushes; PR manager owns draft PR metadata.
  Neither role merges or marks a draft ready. Do not invent mandatory issue/label/milestone rules.

## Shared workflows

The procedures in `.agents/skills/` are canonical. Claude adapters live in
`.claude/agents/`; Codex adapters live in `.codex/agents/`. Keep the adapters thin.
Models and permission modes inherit from the user's session.

Hooks run the shared `scripts/gate_commit.py`. Read `docs/how-to/ai-tooling.md`
for setup, enforcement limits, and supported command forms. Never disable a hook to
get a blocked commit through; fix the finding or report it.

## Project conventions


- Use uv for all project dependency, environment, build, and execution commands; never pip.
- Keep reusable code in `src/`, repeatable utilities in `scripts/`, and tests in `tests/`.
- Ruff line length is 110. Prefer descriptive names and plain `import datetime`.
- Apply the manual version policy in `docs/how-to/versioning.md`; keep `uv.lock` synchronized.
