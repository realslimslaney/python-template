# Customize a generated project

Create a new repository with GitHub's template button, then clone it. Templates copy
files, not repository settings, secrets, variables, or release history.

Change the README heading, description, repository links, Quarto title, and example
commands. Choose your project's license; preserve existing MIT notices when reusing
this starter's code. Update copyright for your additions. Review AGENTS.md and
the default branch setting in `.github/repository-policy.json`.


Rename the distribution in `pyproject.toml`, its console script, `src/python_template/`,
imports in tests, the just `run` recipe, and README examples. Use hyphens for a
distribution name and underscores for its import package. Update the build module
name if it is no longer the normalized distribution name.
Run `uv lock`, `uv sync`, `just check`, and `just build`. Keep the lockfile committed.
The initial customization may retain version 0.1.0 if dependencies do not change.


Review and trust the client hooks as described in [AI tooling](ai-tooling.md).
Follow [versioning](versioning.md) for the new repository's release setup.
Run the complete README setup from a fresh clone before inviting contributors.
