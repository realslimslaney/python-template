# Customize agent instructions and skills

The template's defaults work as checked in. There are no placeholders to fill
before asking an agent to inspect, edit, document, or validate the project.
The normal client installation and hook trust steps are in [AI tooling](ai-tooling.md).

## Change the project rules

1. Edit the root `AGENTS.md`. Record the actual project purpose, source layout,
   setup commands, checks, release policy, and constraints the agent should follow.
   For example, when adding an application to the general template, replace its
   "no application stack" description with the real language and task commands.
2. Keep the text addressed to the agent: "Run just check before finishing" is an
   instruction. Put contributor setup steps and explanations in these docs instead.
3. Run `just agents-sync`. It updates the root `CLAUDE.md` with the full policy.
4. Run `just agents-check` and `just check`. Review and commit both the shared source
   and generated files together, following the repository's normal commit workflow.

Codex loads `AGENTS.md`; Claude loads `CLAUDE.md`. There is no `CODEX.md` entrypoint
in this template. Both root files contain the same complete project instructions,
so neither client depends on following a redirect to discover the basic policy.

## Change a built-in workflow

Edit the matching source in `.agents/skills/`:

- `committer/SKILL.md`: authorized staging, checks, Conventional Commits, and pushes.
- `pr-manager/SKILL.md`: derive PR metadata from the diff and create or update a draft.
- `docs-maintainer/SKILL.md`: maintain README and the four Diataxis sections.

Each file has `name` and `description` frontmatter plus the complete procedure.
Keep the description specific enough for automatic skill selection. The built-in
generator accepts these two fields as plain, unquoted YAML scalars. If you need
additional metadata, extend the generator and its tests alongside the change.

Run `just agents-sync` after editing a source. It writes full copies into
`.claude/skills/` and full native agent definitions into `.claude/agents/` and
`.codex/agents/`. These files are committed and immediately usable by the clients;
running the generator is a maintenance step, not first-use setup.
Edit the shared sources rather than the generated copies, which sync overwrites.
The generator owns only the three named roles and root `CLAUDE.md`.

The defaults inherit the session's model and permissions. If a native role needs
client-specific settings, change `scripts/sync_agent_instructions.py` so those
settings survive the next sync. Keep authorization decisions in the workflow;
do not grant permissions simply to make a role easier to run.

## Try the defaults

Open a fresh client session at the repository root after saving changes.

- In Codex, ask: `Use $docs-maintainer to update the docs for my current changes.`
- In Claude, run: `/docs-maintainer Update the docs for my current changes.`
- Ask: "Use the committer to commit the documentation changes. Do not push."
  This authorizes a local commit of that scope.
- Once a branch is pushed, ask: "Use the PR manager to open a draft PR for this branch."

A direct skill request works without a parent agent. When the main agent delegates,
it supplies the task scope and existing authorization. Codex's native role names
use underscores (`pr_manager`, `docs_maintainer`); skill names use hyphens in both
clients. Claude's native role names use hyphens. Skills also work when a client
cannot launch custom subagents.

Verify that the client loads the root policy and offers the three skills. Claude's
`/memory` and `/agents` views help inspect loaded instructions and roles. If an entry
is missing, confirm that the session is in this checkout, restart it, and check
the client version and project trust settings. `just agents-check` verifies files
on disk; it cannot prove a particular running client has loaded them.

## Add a project-specific skill

Create `.agents/skills/<name>/SKILL.md` with a short name, a description that says
when to use it, and a concrete procedure. Add references or scripts only when the
workflow needs them. For Claude, supply the full skill folder at
`.claude/skills/<name>/`, including its supporting files. The built-in generator
does not copy additional skills automatically; either maintain both folders or
extend its managed roles and tests deliberately.

For discovery rules, see the official
[Codex skills documentation](https://developers.openai.com/codex/skills/),
[Claude skills documentation](https://code.claude.com/docs/en/skills), and
[Claude project memory documentation](https://code.claude.com/docs/en/memory).
