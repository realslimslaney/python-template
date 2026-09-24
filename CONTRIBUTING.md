# Contributing

Follow the README setup, create a focused feature branch, and keep one logical
change per commit. Use Conventional Commits, for example `fix: handle empty input`.
Open a draft PR with the problem, resulting behavior, and checks performed.

Run `just check` before committing. Update the affected Diataxis pages when setup,
commands, configuration, or behavior changes. See [versioning](docs/how-to/versioning.md)
before changing dependencies or public behavior.

Use synthetic fixtures. Keep credentials, private data, machine-specific paths,
and generated build output out of Git. Stage explicit files and preserve unrelated work.

Agent-assisted work follows [AGENTS.md](AGENTS.md). Agent hooks supplement the
instructions; they do not replace human review or GitHub permissions.
