# Agent instructions

## Work in this repository

Read README and the files relevant to the task before editing. Inspect Git status
and preserve unrelated work. Follow existing conventions and keep the requested
change focused. Use synthetic test data; never commit credentials or private data.
Write concise US English, with descriptive names and no em-dashes.

Work on a feature branch. Discover the default branch from origin/HEAD, falling
back to `.github/repository-policy.json`. Create a task branch when starting on
the default branch; do not discard changes to switch branches.

## Python conventions

This repository is a runnable Python package managed with uv. Application code
lives in `src/python_template/`, application tests in `tests/`, repository utilities
in `scripts/`, and their standard-library tests in `tooling_tests/`.

Use uv for environments, dependencies, execution, and builds. Use `uv add`,
`uv remove`, and `uv lock`; keep `uv.lock` committed and synchronized.
Do not run `uv init` in this already-initialized project. Use the src layout,
Ruff's configured 110-character limit, and plain `import datetime`.

`pyproject.toml` owns the version. Increase minor for features or dependency
additions/removals, patch for fixes or dependency updates, and major for incompatible
public interfaces, including before 1.0. Run `uv lock` after a version change.
Documentation, formatting, and repository-tooling maintenance without application
or dependency changes need no package bump. Use `docs/how-to/versioning.md`
for release steps; do not publish a package or release without authorization.

## Validate and document changes

Run commands from the repository root. `just` lists the available recipes.
- `just setup`: synchronize the uv environment from the committed lockfile.
- `just run`: run the example application.
- `just lint`, `just fmt-check`, `just test`: application lint, format, and test checks.
- `just fmt`: apply formatting; inspect its diff.
- `just build`: build the wheel and source distribution after packaging changes.
- `just tooling-test`: exercise hooks and repository tooling.
- `just docs-check`: validate local links and repository configuration.
- `just docs-build`: render the Quarto site.

Run `just check` before reporting completion. A missing tool or failing command is
a limitation to report, not a passing check. Fix failures caused by the change;
avoid unrelated repairs. Add regression tests when behavior changes warrant them.

Update README when setup or public usage changes. Put guided learning in
`docs/tutorials/`, task instructions in `docs/how-to/`, exact interfaces and
commands in `docs/reference/`, and design reasoning in `docs/explanation/`.
Quarto discovers Markdown pages in those folders. Add a relevant incoming link
for new pages. Keep rendered `docs/_site/` and local environments out of commits.

## Use the workflow roles

- `docs-maintainer` updates documentation for the actual diff before PR preparation.
- `committer` stages focused changes and creates Conventional Commits after user
  authorization. It pushes only within authorized publication scope.
- `pr-manager` prepares or updates a draft PR for an already-pushed branch using
  the diff and validation results. It does not commit, push, merge, or mark ready.

Delegate authorized commits to the committer when custom agents are available.
Pass the user's authorization verbatim, the intended file scope, validation results,
and whether pushing is authorized. Use the matching skill directly when custom
agents are unavailable. A role already handling its own workflow must not delegate
the same task recursively. Reuse authorization already given within its scope;
do not ask for it again. Without commit or publication authorization, finish the
edits and checks before asking for the missing approval.

Discover skills in `.agents/skills/` (Codex) or `.claude/skills/` (Claude).
Custom agents live in `.codex/agents/` and `.claude/agents/`; models and permissions
inherit from the session. Use the native role name exposed by the client
(`pr_manager` and `docs_maintainer` in Codex).

Stage explicit paths. Never bypass hooks, force-push, amend published commits, or
merge without authorization. Run commits as standalone `git commit -m "type: summary"`
or `git commit -F message-file` commands from the repository root, after staging
in a separate call. The hook validates the staged snapshot; do not use `-a`,
commit pathspecs, combined commands, or Git configuration overrides in commit calls.
Fix or report gate failures instead of disabling the gate.

When changing these instructions, edit `AGENTS.md`. When changing a workflow,
edit its `.agents/skills/<role>/SKILL.md`. Run `just agents-sync` and include the
generated client files in the change. `just agents-check` detects drift.
