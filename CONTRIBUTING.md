# Contributing

Use Python 3.10 or newer. Install with `python -m pip install uv` and
`uv sync --frozen --all-groups`. Use the commands below for the full local check
set. Do not commit source content, cookies, API keys, local database files, or
personal reports. Keep Agent Reach as an upstream-owned dependency and add
parity checks whenever its adapter changes. New research assertions must be
source-backed, and any status must state exactly what the check establishes.
# Development checks

The locked development tools and CI use the same local commands:

```sh
uv sync --frozen --all-groups
uv run --frozen ruff check src tests scripts
uv run --frozen mypy
uv run --frozen coverage run -m pytest -v --junitxml=pytest-results.xml
uv run --frozen coverage report --fail-under=80
uv run --frozen python -m unittest discover -s tests -v
uv run --frozen python scripts/smoke_installed_wheel.py
```

The wheel smoke script builds a wheel, installs it into a temporary virtual
environment with a separate data directory and no `PYTHONPATH`, and exercises
the installed CLI and MCP tool listing. CI retains the pytest and coverage XML
reports as workflow artifacts.
