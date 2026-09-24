# Maintain and publish documentation

Install [Quarto](https://quarto.org/docs/get-started/) separately from your application's
dependencies. Run `just docs` for preview or `just docs-build` for a static site.

Add a Markdown page to the appropriate Diataxis directory. Link it from an existing
page; the sidebar includes category pages automatically. Run `just docs-check` to
validate local links and `just docs-build` to check the rendered site. Keep executable
examples as fenced text unless the project intentionally adds a notebook runtime.

To publish to GitHub Pages, enable Pages for the repository and follow
[Quarto's GitHub Pages guide](https://quarto.org/docs/publishing/github-pages.html).
Run `quarto publish gh-pages docs` only when you intend to publish the site.
CI builds documentation but does not deploy it. For project sites, configure the
correct site URL before publishing. Never add private documentation to a public site.
