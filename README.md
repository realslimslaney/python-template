# Python Template

A minimal Python package managed with uv, with Ruff, pytest, just, and Quarto.

Use GitHub's **Use this template** button to create a new repository, then clone it.
Start on a feature branch: `git switch -c chore/customize-template`.

## Get started

Follow the [step-by-step first-project tutorial](docs/tutorials/first-project.md)
to create your repository, install the tools, run the checks, and open your first PR.
For an existing copy, use the [customization how-to](docs/how-to/customize.md).

## Install the tools

- [Git](https://git-scm.com/downloads) and [just](https://just.systems/man/en/).
- [Quarto](https://quarto.org/docs/get-started/), installed as a standalone CLI.
- Python 3.13+ for repository tooling and commit hooks. On Windows, expose `python` on PATH;
  on macOS/Linux, expose `python3` and provide `python` for Claude command hooks.
- [uv](https://docs.astral.sh/uv/getting-started/installation/) for Python, dependencies,
  environments, and builds. `uv python install 3.13` installs the project's interpreter.
  Install a system Python as well if needed to make the hook's Python command available.

On Windows, just uses PowerShell. On macOS/Linux it uses the default shell.
Verify `git --version`, `just --version`, `quarto --version`, and your Python command first.

## Start working

```sh
uv sync
just run
just check
just docs
```

The first run builds the documentation as part of the checks. Preview prints a local URL;
stop it with Ctrl+C. Generated files are ignored.

## Make it yours

Follow [customization](docs/how-to/customize.md) to change the project name, links,
license, and configuration. Read [versioning](docs/how-to/versioning.md) before dependency
changes or releases. The [command reference](docs/reference/commands.md) describes each recipe.

The Quarto site has all four Diataxis sections: tutorials, how-to, reference, and explanation.
Start with [your first change](docs/tutorials/first-project.md).

## AI workflows

Ready-to-use project instructions live in [AGENTS.md](AGENTS.md) for Codex and
[CLAUDE.md](CLAUDE.md) for Claude. Both clients have complete committer, PR manager,
and docs maintainer agents and discoverable skills.
[Customize the agent defaults](docs/how-to/customize-agent-instructions.md) as your project grows. Review and trust their
runtime hooks using [the setup guide](docs/how-to/ai-tooling.md). Agents require explicit
commit authorization and preserve authorization already given for the task.

CI runs on Windows and Ubuntu. Documentation builds locally and in CI; publishing the site
is an [opt-in step](docs/how-to/documentation.md).

## Initialize a uv project from scratch

This template already has `pyproject.toml`: use `uv sync` here, not `uv init`.
To create the same package shape in a new directory instead:

```sh
uv init --package --build-backend uv --python 3.13 --no-workspace my-project
cd my-project
uv add --dev ruff pytest
uv sync
uv run my-project
uv build
```

`uv init` creates a package; it does not add this template's docs, just recipes, or agents.
Copy those from the template if starting from scratch. In an existing general repository,
use `uv init --package --build-backend uv --python 3.13 --name my-project --no-readme --vcs none .`
before adapting its just and CI commands.

Manage dependencies with `uv add package-name`, `uv add --dev package-name`, and
`uv remove package-name`. Update resolved versions with `uv lock --upgrade`, then follow
the manual version policy and commit both metadata and the lockfile. Use `uv run` for tools;
no environment activation or pip commands are needed.

## License

MIT. Preserve the supplied notice for reused template code and choose an appropriate license for your additions.
