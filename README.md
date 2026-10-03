# VAJRA

**Evidence before answers.** Vajra is a local-first research workbench that records searches, fetched sources, exact evidence passages, claim status, and replayable reports. It keeps discovery separate from verification and marks the limits of what a source proves.

## Current implementation

- `vajra research QUESTION` runs a bounded search/fetch/evidence workflow, saves its trace in SQLite, and exports a Markdown report plus `research.json`.
- Search uses the optional DDGS metasearch adapter (`pip install -e ".[search]"`). Search results are leads; only fetched page text enters the evidence ledger.
- `vajra doctor` checks the database, installed optional search/MCP dependencies, and the installed Agent Reach CLI. Agent Reach channel names and health are read dynamically from `agent-reach doctor --json`.
- `vajra upstream-check` asks Agent Reach to check for updates without installing them.
- `vajra replay ID` reconstructs the recorded JSON trace. `vajra audit ID` checks citation IDs and quoted spans against the stored source text.
- `vajra mcp` starts the optional local stdio MCP server (`pip install -e ".[mcp]"`). The MCP server is read-only apart from running an explicitly requested research job.

`benchmarks/score.py` scores saved traces against a human-adjudicated corpus for exact evidence coverage and trace integrity; it does not score factual truth or semantic entailment. See `benchmarks/README.md`.

## Install and run

### Install the experimental build from GitHub

The source repository is public. This is an early experimental build and is **not production-ready**; search can fail and its evidence excerpts do not verify factual truth.

```powershell
python -m pip install uv
uv tool install --from "git+https://github.com/mishraxram/vajra.git" --with "ddgs==9.16.0" --with "mcp==2.2.0" vajra-research
uv tool update-shell
vajra doctor
```

Restart PowerShell if `vajra` is not found after updating the tool path. Then run:

```powershell
vajra research "Your actual research question" --mode standard
```

The install target is the distribution name `vajra-research`; it installs the `vajra` executable. The optional dependencies enable search and MCP support.

Reports are saved under `%LOCALAPPDATA%\Vajra\reports`. The PyPI package has not been published; this command installs directly from GitHub.

### Install from a local checkout

```powershell
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
