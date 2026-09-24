# Set up Claude and Codex

Install Python 3.13+, Git, just, and Quarto. On Windows, make `python` available on
PATH; on macOS/Linux, provide `python3` (and `python` for Claude's command hook).
Claude on Windows uses Git Bash. The Python starter also needs uv and `uv sync`.

Open the repository root in your client. Codex loads AGENTS.md; Claude loads the
root CLAUDE.md. Both contain complete defaults. Skills are checked in at
`.agents/skills/` for Codex and `.claude/skills/` for Claude. No generation step is
needed to use them. See [customizing agent instructions](customize-agent-instructions.md)
for invocation examples and how to update the defaults. Review the repository-local
hook configuration and approve trust through the client's normal controls. Codex
project hooks require a trusted project and trusted hook definitions. Restart a client
if newly added custom agents are not discovered. No user-global configuration is changed.

Ask for documentation maintenance before a PR. When ready, explicitly authorize
the commit and, separately or in the same instruction, any intended push. The parent
passes your words to the committer. The PR manager works only on the pushed branch.
Existing authorization is reused within its scope.

## Hook contract

Both clients run `scripts/gate_commit.py` with a PreToolUse JSON payload on stdin.
It recognizes `tool_input.command` and `tool_input.cmd`, uses the tool working
directory when supplied, and returns the clients' PreToolUse denial JSON on stdout.
It exits successfully after returning a decision so shell exit-code translation cannot hide a denial.
Malformed input, missing check tools, errors, and check timeouts are denied.

Use a standalone `git commit -m "type: summary"` or `git commit -F message-file`
with the shell tool's working directory set to the repository. `git -C path commit`
is supported. Stage in a separate call. Combined shell commands, commit pathspecs,
`-a`, and Git configuration overrides are rejected for commit calls because they can
change the index or target after validation. `--dry-run` remains a checked commit call.

The gate blocks default-branch or detached-HEAD commits, `--no-verify`/`-n`, and failed
`just check` runs. It exports the staged files to a temporary directory and runs
checks there, leaving the checkout untouched. Python dependency changes additionally
require a staged version increase and a synchronized lockfile.

Approval and agent delegation are instruction-level requirements: a shell payload
cannot prove that a human authorized a commit. Wrapper scripts, Git aliases, external
Git clients, and API commits are outside this command gate. Do not use them to bypass it.
A disabled, untrusted, or unavailable client hook provides no enforcement; CI still runs.

See the [Codex hooks documentation](https://learn.chatgpt.com/docs/hooks) and
[Claude hook reference](https://code.claude.com/docs/en/hooks) for client setup.
Run `just tooling-test` to exercise the shared gate without creating a real project commit.
