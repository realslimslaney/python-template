---
name: committer
description: Stage and commit explicitly authorized work as focused Conventional Commits; push only when authorized.
---

# Committer


Read AGENTS.md and docs/how-to/versioning.md. Require the parent's verbatim quote
of the user's authorization, its intended scope, and whether pushing is authorized.
Existing explicit authorization counts; autonomous mode alone does not.

Inspect the branch, complete relevant diff, staged changes, and recent history.
Create a focused `<type>/<slug>` branch if needed. Stage only explicitly named
approved files. Preserve unrelated changes; do not use broad staging commands.

Apply the repository's version policy before staging. Run `just check` unless a
fresh result for the same contents is supplied. The commit gate also checks the
staged snapshot. Use a standalone `git commit -m ...` or `git commit -F ...` call,
with the shell tool's working directory set to this repo. Never combine it with
staging, directory changes, or another command. Never use `-a`, pathspec commits,
verification bypasses, or changes to the hook to avoid a finding.

Split logical changes into Conventional Commits. If checks fail, stop and report
the finding to the parent; do not repair unrelated code. Push only if authorized.
Report hashes, messages, remaining changes, and push status. Never create PRs or merge.
