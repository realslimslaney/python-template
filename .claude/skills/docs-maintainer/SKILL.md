---
name: docs-maintainer
description: Update README and Diataxis documentation to match code or workflow changes. Use for documentation maintenance and before PR preparation.
---

# Maintain project documentation

Read AGENTS.md or CLAUDE.md, README, and the relevant docs. Inspect the intended
change: use the parent's file scope when supplied, otherwise compare the current
branch with its base and include relevant uncommitted changes. Inspect the actual
commands and source before documenting behavior. Handle a direct documentation
request without requiring a parent handoff.

## Make the documentation match

- Update README for installation, first use, or public workflow changes.
- Use `docs/tutorials/` for a complete learning exercise with a visible outcome.
- Use `docs/how-to/` for task-focused steps, prerequisites, and verification.
- Use `docs/reference/` for exact commands, options, configuration, and interfaces.
- Use `docs/explanation/` for reasons and tradeoffs.
- Link new pages from a relevant existing page. The Quarto sidebar discovers
  Markdown pages in these four folders automatically.
- Keep instructions for people in docs. Keep AGENTS.md, CLAUDE.md, and skill bodies
  addressed to the agent, with working defaults rather than setup placeholders.

Edit documentation, README, CONTRIBUTING, and Quarto configuration as needed for
the requested scope. Report implementation or agent-policy defects to the parent
or user rather than silently changing behavior. Do not invent commands, guarantees,
test results, or features. Avoid credentials, private data, and machine-specific paths.

Run `just docs-check` and `just docs-build`; inspect the rendered output when layout
changes. Report pages changed, checks performed, and unresolved documentation gaps.
Do not commit, push, create a PR, or deploy documentation in this role.
