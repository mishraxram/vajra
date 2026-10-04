# Current system baseline

This document records the Phase 0 inspection of the `phase-1-stabilization`
checkout at `bafad95`.

## Modules and public entry points

- `src/vajra/cli.py`: argparse commands (`welcome`, `doctor`, `research`,
  `replay`, `audit`, `mcp`, and upstream update check); creates the local store.
- `src/vajra/engine.py`: research planning, bounded search/fetch orchestration,
  passage selection, trace construction, audit, and report export.
- `src/vajra/providers/`: DDGS search, its federated wrapper, and a read-only
  Agent Reach health/update adapter.
- `src/vajra/fetch.py` and `security.py`: public URL checks, bounded HTTP
  retrieval, HTML extraction, untrusted-text marking, and evidence selection.
- `src/vajra/mcp_server.py`: local stdio MCP server and four registered tools.
- `src/vajra/store.py`: SQLite run/source/evidence/claim/conflict persistence.
- `src/vajra/models.py` and `budget.py`: data records and overlapping source
  text chunking.

The installed console entry point is `vajra = vajra.cli:main`. The supported
Python range is 3.10+, with direct runtime dependencies pinned in
`pyproject.toml` and a committed `uv.lock`.

## Data flow and persistence

The CLI or MCP tool invokes the research engine. The engine plans bounded query
sets, calls synchronous providers in bounded worker threads, fetches selected
public URLs, extracts text, selects exact passage offsets, audits trace links,
and persists the trace in SQLite. Reports and JSON traces are written beneath
the configured data directory. The default is `%LOCALAPPDATA%\\Vajra` on
Windows and `~/.local/share/vajra` elsewhere; `VAJRA_DATA_DIR` or `--data-dir`
can override it.

## Trust boundaries

Search results and retrieved or externally supplied text are untrusted data.
URL validation rejects non-HTTP(S), local/private targets, credentials, and
non-public DNS results. Fetches validate redirects and bound time, size, and
content type. The MCP server uses local stdio and can initiate public web
research when invoked. Agent Reach remains a separate installation and owns
its own authentication/session state; Vajra's adapter invokes its read-only
doctor/version/update-check commands with `shell=False`.

## Baseline failure modes

- Confirmed: with `ddgs` installed, `DDGSSearchProvider.health()` returns
  `None`; `vajra doctor` then raises `TypeError` while unpacking the result.
- Confirmed: the existing suite is unittest-based; pytest, coverage, Ruff,
  mypy, and a clean installed-wheel smoke procedure are absent from the current
  environment/repository configuration.
- Existing provider/engine tests cover bounded research and extraction, but the
  suite does not exercise the doctor's health paths or a freshly installed
  wheel's CLI and MCP entry points.
- Agent Reach reports capability health; the adapter does not execute platform
  searches or reads. Health is not research execution.
- Passage ranking is lexical overlap, and claim verification is limited to
  exact span integrity. Publisher authority, source independence, and factual
  truth are not established.
- SQLite persistence has no explicit owner-only permission or encryption
  mechanism in this baseline.

See [`baseline.json`](baseline.json) for recorded commands and outcomes.
