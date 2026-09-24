# Make your first change

Use GitHub's **Use this template** button to create your repository, then clone it.
Install the tools listed in the README. Create a branch with `git switch -c docs/first-change`.

Run these commands from the repository root:

```sh
uv sync
just run
just check
```

Open this tutorial and replace its title with a title meaningful to your project.
Run `just docs`, open the preview address, and find the page in Tutorials.
Stop preview with Ctrl+C, then run `just check` again.

Inspect `git diff`. Stage this page by its explicit path, commit it with a message
such as `docs: describe the first project change`, and push your feature branch.
Open a draft pull request describing the change and checks. If an agent performs
those actions, give it explicit authorization and use the supplied workflows.

Next, follow [customization](../how-to/customize.md) to rename the starter.
