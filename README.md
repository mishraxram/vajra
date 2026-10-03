# VAJRA

**Evidence before answers.** A local-first research CLI and MCP server that saves the search trail, fetched sources, exact evidence passages, and an auditable report.

[![CI](https://github.com/mishraxram/vajra/actions/workflows/ci.yml/badge.svg)](https://github.com/mishraxram/vajra/actions/workflows/ci.yml)
[![MIT License](https://img.shields.io/github/license/mishraxram/vajra)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)

> **Experimental:** search engines and websites can block requests. A passing citation audit verifies that a quote matches fetched text; it does not prove the claim is true. Read [the release audit](RELEASE_AUDIT.md) before using this for consequential decisions.

## Install and run

Requires Python 3.10 or newer. Install `uv` once, then install VAJRA directly from this public repository:

```powershell
python -m pip install uv
uv tool install git+https://github.com/mishraxram/vajra.git
```

Restart the terminal if `vajra` is not on `PATH`, then:

```powershell
vajra doctor
vajra research "What evidence supports and challenges your research question?" --mode standard
```

The research command prints the report and trace paths. By default, reports are saved in `%LOCALAPPDATA%\Vajra\reports` on Windows and `~/.local/share/vajra/reports` on macOS/Linux. Change the location with `--data-dir PATH` or `VAJRA_DATA_DIR`.

The package installs search and MCP dependencies by default, so the same installation works for the CLI and MCP-compatible AI clients. No API key or paid search account is required. Public search backends may rate-limit or block requests.

## Connect an AI coding agent

VAJRA exposes a local stdio MCP server. Add this server to an MCP-compatible client's MCP configuration (the exact file location varies by client):

```json
{
  "mcpServers": {
    "vajra": {
      "command": "vajra",
      "args": ["mcp"]
    }
  }
}
```

Restart the client and ask it to research a question with Vajra. The server exposes research, replay, audit, and Agent Reach health tools; it does not expose arbitrary shell or local-file access. See [MCP setup and tool details](MCP.md).

## What it does

- Plans bounded primary and counterevidence searches for `fast`, `standard`, `deep`, and `forensic` runs.
- Tries DDGS automatic search, then DuckDuckGo, Bing, and Brave backends if the previous route errors or returns no hits. Every route and failure is recorded.
- Fetches candidate public pages with URL, redirect, response-size, and timeout controls; extracts text without running page scripts.
- Stores fetched text, exact quote offsets, metadata, hashes, query history, failures, and a replayable JSON trace in SQLite.
- Marks a run `partial` when a query/fetch fails or it collects fewer than the mode's source minimum. It never labels a one-source standard run complete.
- Dynamically reads Agent Reach's current channels and health. Agent Reach remains upstream-owned; its platform-specific content tools are not replaced by Vajra.

Useful commands:

```text
vajra doctor
vajra research "QUESTION" --mode forensic
vajra audit RESEARCH_ID
vajra replay RESEARCH_ID
vajra upstream-check
```

## Current limits

VAJRA is an evidence collection and citation-audit workbench, not an autonomous truth oracle. It does not yet perform semantic entailment, authoritative-source ranking, independent-source adjudication, or reliable general contradiction resolution. Evidence passages are source assertions. Check the sources yourself, especially for medical, legal, financial, or safety decisions.

Search coverage depends on external public engines and websites. Captchas, rate limits, robots/access controls, network policy, and HTTP 403/429 responses can reduce coverage. Failures are written into the trace and lower the run status. DNS rebinding risk and broader security gaps are documented in [SECURITY.md](SECURITY.md) and [THREAT_MODEL.md](THREAT_MODEL.md).

## Develop and verify

```powershell
python -m pip install uv
uv sync --frozen
uv run python -m unittest discover -s tests -v
```

See [architecture](ARCHITECTURE.md), [provider details](PROVIDER_GUIDE.md), [benchmark harness](benchmarks/README.md), [contributing](CONTRIBUTING.md), and [third-party notices](THIRD_PARTY_NOTICES.md).
