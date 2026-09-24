set windows-shell := ["powershell.exe", "-NoLogo", "-NoProfile", "-Command"]

python := if os() == "windows" { "python" } else { "python3" }

default:
    @just --list

# Validate repository tooling without application dependencies.
tooling-test:
    uv run --locked python -m unittest discover -s tooling_tests -v

# Check links, configuration, and the shared agent adapters.
docs-check:
    uv run --locked python scripts/check_repo.py

# Preview documentation without opening a browser.
docs:
    quarto preview docs --no-browser

# Render the documentation website.
docs-build:
    quarto render docs

setup:
    uv sync --locked

run:
    uv run --locked python-template

lint:
    uv run --locked ruff check .

fmt:
    uv run --locked ruff format .

fmt-check:
    uv run --locked ruff format --check .

test *args:
    uv run --locked pytest {{args}}

build:
    uv build

check: lint fmt-check test tooling-test docs-check docs-build
