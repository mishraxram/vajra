<p align="center">
  <img src="assets/vajra-wordmark-banner.png" alt="VAJRA — The Open Agent Research Ecosystem" width="100%" />
</p>

<p align="center"><strong>Evidence before answers.</strong><br />A local-first research CLI, reusable agent skill, and MCP server.</p>

<p align="center">Search → fetch → preserve exact passages → audit the trail</p>

[![CI](https://github.com/mishraxram/vajra/actions/workflows/ci.yml/badge.svg)](https://github.com/mishraxram/vajra/actions/workflows/ci.yml)
[![MIT License](https://img.shields.io/github/license/mishraxram/vajra)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)

> **Experimental:** search engines and websites can block requests. A passing citation audit verifies that a quote matches fetched text; it does not prove the claim is true. Read [the release audit](RELEASE_AUDIT.md) before using this for consequential decisions.

## Install and run

Requires Python 3.10 or newer. Install `uv` once, then install VAJRA directly from this public repository:

```powershell
python -m pip install uv
uv tool install --from git+https://github.com/mishraxram/vajra.git vajra-research
```

The install target is the Python distribution name, `vajra-research`; the command it adds is still `vajra`.

Restart the terminal if `vajra` is not on `PATH`, then:

```powershell
vajra doctor
vajra research "What evidence supports and challenges your research question?" --mode standard
```

For a guided terminal run on Windows, use `scripts/vajra-demo.ps1`. On macOS/Linux, use `bash scripts/vajra-demo.sh`. Both scripts prompt for a question (or accept it as an argument) and run actual Vajra research; set `VAJRA_MODE=fast`, `standard`, `deep`, or `forensic` to choose a mode.

The research command prints the report and trace paths. By default, reports are saved in `%LOCALAPPDATA%\Vajra\reports` on Windows and `~/.local/share/vajra/reports` on macOS/Linux. Change the location with `--data-dir PATH` or `VAJRA_DATA_DIR`.

The package installs search and MCP dependencies by default, so the same installation works for the CLI and MCP-compatible AI clients. No API key or paid search account is required. Public search backends may rate-limit or block requests.

## Install into your AI CLI

To give a compatible coding agent reusable VAJRA instructions, install the skill to all supported clients detected by the open Agent Skills installer:

```powershell
npx skills add mishraxram/vajra --skill vajra-research --global --yes --agent '*'
```

The skill is real workflow guidance: it tells an agent to run VAJRA research, inspect the run status, and audit the saved evidence. The `uv tool install` command above installs the executable and MCP server; the skill command installs instructions. For a one-message AI-assisted setup, send your agent: `Install VAJRA for me: https://raw.githubusercontent.com/mishraxram/vajra/master/INSTALL.md`.

MCP clients can call VAJRA's research, replay, citation-audit, and Agent Reach status tools. See [tested client setup examples](AGENT_INTEGRATIONS.md).

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
