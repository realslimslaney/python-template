---
name: pr-manager
description: Prepare or update a GitHub draft pull request from a pushed branch and its diff. Use when asked to open or revise a PR.
---

# Prepare a draft pull request

Read AGENTS.md or CLAUDE.md. Use the current request or the parent's handoff to
identify the intended PR and authorization. A direct request to open a PR is
sufficient; a prewritten title or body is not required. Reuse existing authorization.
Do not delegate this workflow to another PR manager.

## Inspect the branch

Discover the repository, remote, default branch, and current feature branch.
Inspect Git status, commits, and the diff against the base. Require a clean tracked
working tree and confirm the remote branch contains the current HEAD. If changes
are uncommitted or unpushed, report the specific blocker to the user or parent;
do not commit, push, or silently omit those changes.

Look for an existing open PR for this branch before creating one. Read the PR
template and relevant documentation. Use the docs-maintainer's results if supplied;
otherwise check documentation against the diff and report missing updates before
publication. Verify the available validation evidence rather than inventing results.

## Write and publish

Derive a concise Conventional Commit title and body from the final diff. Lead
with the problem and resulting behavior. Include relevant checks and material
limitations. Link an issue only if it is known and relevant; use closing keywords
only when the change resolves it. Do not invent required labels, milestones,
reviewers, project IDs, or issues.

Create a draft PR when authorized. Update an existing PR's title and body in scope
without changing its draft/ready state. Use an available GitHub connector or `gh`;
for multiline CLI bodies, write a temporary file and pass `--body-file`. If
publication is not authorized, finish the proposed title and body for review first.

Read back the PR to verify its base, head, title, body, draft state, and URL.
Return the URL and validation status, distinguishing local checks from CI.
Do not modify source files, commit, push, merge, mark ready, or change repository
settings. Do not request reviewers or send separate messages unless requested.
