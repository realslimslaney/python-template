# Why this structure

The foundation keeps repeatable tasks in just, longer guidance in a Quarto site,
and narrowly scoped agent workflows beside the code. Application dependencies belong
to the project that needs them; finance, climate, notebook, and UI packages are not defaults.

Documentation follows [Diataxis](https://diataxis.fr/): tutorials teach through a complete
example, how-to pages solve a specific task, reference records exact behavior, and
explanation discusses decisions. The website sidebar discovers each category's pages.

The Python starter uses a src layout to exercise the installed package instead of
accidentally importing directly from the checkout. The general starter has no
application manifest. Its Python scripts are dependency-free repository tooling.

Both use standalone Quarto so the documentation setup remains independent of the
application's language. Rendered output is disposable and ignored by Git.

Agent policies and procedures have shared sources and complete, checked-in client
copies. Each client discovers usable instructions and skills in its native folders;
`just agents-sync` refreshes the copies and validation detects drift.
Commit hooks validate a copy of the Git index so unstaged fixes cannot make a broken
commit look healthy. Hooks are workflow safeguards, not a security boundary against
arbitrary shell programs. CI independently runs the same project checks.
