# Version a Python change

`pyproject.toml` is authoritative, beginning at 0.1.0. Change its version in the same
commit as the change, then run `uv lock` and stage both files.

- Increase minor for new features or dependency additions/removals.
- Increase patch for fixes, changed dependency constraints, or resolved dependency updates.
- Increase major for incompatible public interfaces, including before 1.0.
- Documentation, formatting, and metadata-only lockfile changes need no bump.

Include runtime, optional, build, and development dependencies in this policy.
The gate compares staged dependency metadata and lockfile package resolutions with
HEAD, excluding the local package version and lockfile formatting. A meaningful
dependency change needs a numeric version increase. The reviewer checks whether
the selected major/minor/patch level matches the change; the gate does not infer intent.

Run `uv lock`, `just check`, and `just build`. `just check` validates lock freshness.
When you intend to release, use the package version for a `vX.Y.Z` Git tag and a
GitHub release after review. No release or PyPI upload occurs automatically.

To adopt release-please later, replace the manual policy with a Python release
strategy and lockfile-refresh workflow together, then update the gate policy and agents.


## Choosing another policy

Both policies use semantic versions and Conventional Commits. They differ in when
the version changes: alongside implementation, or in a dedicated release PR.
Use one authoritative policy at a time so agents and automation do not compete.

Release-please supports Python's `pyproject.toml` and changelog. A uv project also
needs `uv lock` after the release PR changes its package version; add that update to
the release-PR workflow and retain `uv sync --locked` in CI. Do not assume the Python
strategy refreshes `uv.lock`. PyPI publishing is a separate, explicitly configured job.

See [release-please](https://github.com/googleapis/release-please-action) and
its [Python strategy](https://github.com/googleapis/release-please/blob/main/src/strategies/python.ts).
