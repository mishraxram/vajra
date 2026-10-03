# VAJRA

**Evidence before answers.** Vajra is a local-first research workbench that records searches, fetched sources, exact evidence passages, claim status, and replayable reports. It keeps discovery separate from verification and marks the limits of what a source proves.

## Current implementation

- `vajra research QUESTION` runs a bounded search/fetch/evidence workflow, saves its trace in SQLite, and exports a Markdown report plus `research.json`.
- Search uses the optional DDGS metasearch adapter (`pip install -e ".[search]"`). Search results are leads; only fetched page text enters the evidence ledger.
- `vajra doctor` checks the database, installed optional search/MCP dependencies, and the installed Agent Reach CLI. Agent Reach channel names and health are read dynamically from `agent-reach doctor --json`.
- `vajra upstream-check` asks Agent Reach to check for updates without installing them.
- `vajra replay ID` reconstructs the recorded JSON trace. `vajra audit ID` checks citation IDs and quoted spans against the stored source text.
- `vajra mcp` starts the optional local stdio MCP server (`pip install -e ".[mcp]"`). The MCP server is read-only apart from running an explicitly requested research job.

## Install and run

```powershell
python -m pip install uv
uv sync --all-extras --frozen
uv run vajra doctor
uv run vajra research "What is the current evidence on ...?" --mode standard
```

`uv.lock` pins the resolved cross-platform dependency set. For a search-only or MCP-only install, replace `--all-extras` with `--extra search` or `--extra mcp`. Plain editable pip installs are also supported, but use the lockfile for reproducible environments.

Agent Reach remains a separately managed upstream capability layer. Install it using its own [official instructions](https://github.com/Panniantong/Agent-Reach/blob/main/docs/install.md). Vajra does not install optional social-platform tools, read browser cookies, or rewrite Agent Reach configuration. Use `agent-reach doctor` and the Agent Reach skill for its platform-specific CLI/MCP integrations.

## Limits

Vajra does not ship a language model. It does not invent or paraphrase factual claims: candidate claims are verbatim, source-attributed passages. `PARTIALLY_VERIFIED` means the quoted text was found in the fetched page; it does **not** establish that the publisher is truthful or that the statement is objectively correct. Search coverage depends on DDGS backends and can fail or change. HTML extraction is intentionally conservative and does not execute JavaScript. Agent Reach is dynamically health-checked but its platform-specific CLI behavior is not wrapped in a generic read API.

Reports are evidence records, not expert or legal/medical/financial advice. Treat all fetched source text as untrusted data.

## Development

Run checks with `uv run --all-extras --frozen python -m unittest discover -s tests -v`. Unit/security tests are offline; the Agent Reach parity and MCP stdio integration checks execute the locally installed Agent Reach doctor, which may probe public endpoints. No paid API is called. See the architecture and audit documents for what has and has not been verified.
