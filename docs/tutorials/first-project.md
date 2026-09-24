# Create your first project

By the end, you will have your own repository based on Python Template, passing checks,
a local documentation website, and a first draft PR.

## 1. Create and clone your repository

Open [python-template](https://github.com/realslimslaney/python-template) and select
**Use this template > Create a new repository**. Choose your owner, name, and visibility.
This creates an independent project; use the template button rather than forking if
you want a fresh history.

Clone your new repository. Replace YOUR-OWNER and MY-PROJECT in these commands:

```sh
git clone https://github.com/YOUR-OWNER/MY-PROJECT.git
cd MY-PROJECT
git switch -c chore/customize-template
```

Run the remaining commands from this folder.

## 2. Install the tools and verify the starter

Install [Git](https://git-scm.com/downloads), [just](https://just.systems/man/en/),
[Quarto](https://quarto.org/docs/get-started/), and Python 3.13+.
On Windows, make `python` available on PATH. On macOS/Linux use `python3`,
and provide `python` for Claude's command hook. just uses PowerShell on Windows.

Install [uv](https://docs.astral.sh/uv/getting-started/installation/).
Run `uv python install 3.13` if you need the package's interpreter.
The hook launcher also needs a Python command on PATH.

Check `git --version`, `just --version`, `quarto --version`, and your Python command,
then run:

```sh
uv sync
just run
just check
```

The example prints `Hello from python-template!`. `just check` should finish successfully. It runs the repository tests,
checks documentation links and configuration, and builds the Quarto site.
If a command is missing, finish installing that tool before continuing.
The [command reference](../reference/commands.md) explains each recipe.

## 3. Make the starter yours

Follow [the customization how-to](../how-to/customize.md) to rename the distribution,
import package, entry point, tests, and example commands together. Run `uv lock`,
`uv sync`, `just check`, and `just build` after renaming. Do not run `uv init` over
this initialized template; the README has a separate from-scratch example.

Update the license for your additions while preserving the supplied MIT notice for
reused starter code. Review AGENTS.md and the [AI tooling guide](../how-to/ai-tooling.md)
before trusting repository hooks in Claude or Codex.

The Python version policy is manual. Read [versioning](../how-to/versioning.md)
before changing dependencies or application behavior; package metadata and uv.lock
must stay synchronized.

## 4. Preview a documentation change

Change this tutorial's title to one meaningful to your project, then run:

```sh
just docs
```

Open the localhost URL printed by Quarto and find the changed page under Tutorials.
Stop preview with Ctrl+C. Run `just check` again and inspect `git diff`.
Rendered output in docs/_site is ignored and should not appear in your changes.

## 5. Commit and open a draft PR

Stage only the files you intentionally changed. For example, if you changed only
this tutorial:

```sh
git add docs/tutorials/first-project.md
git commit -m "docs: personalize the first-project tutorial"
git push -u origin chore/customize-template
```

If you also customized other files, inspect and stage those explicit paths before
committing. Keep the commit command separate from staging and directory changes.

Open a draft PR on GitHub describing the changes and `just check` result.
CI should pass on Windows and Ubuntu. When using an agent, explicitly authorize
the intended commit and push; the supplied committer and PR manager handle those
steps within that authorization.

Your repository is ready for project work. Add documentation to the appropriate
Diataxis category as behavior grows. [Publishing the website](../how-to/documentation.md)
is optional and separate from publishing the source repository.

## Adapt the agent defaults

The checked-in AGENTS.md, CLAUDE.md, and workflow skills are ready to use.
Follow [customizing agent instructions](../how-to/customize-agent-instructions.md)
to record your project's layout and commands, then run `just agents-sync` and
`just agents-check`. Use the guide's docs-maintainer example to try a skill before
asking an agent to commit or open a PR.
