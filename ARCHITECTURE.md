# Architecture

```text
CLI / local MCP stdio
         |
Research planner and bounded run loop
    |                    |
SearchProvider       AgentReachProvider (health/capabilities)
    |                    |
DDGS (optional)      agent-reach doctor --json (upstream-owned)
    |
Safe fetch + conservative HTML/text extraction
    |
Exact passage evidence + candidate claims + citation audit
    |
SQLite run ledger -> research.json + Markdown report
```

`ResearchStore` is the durable source of replay data. The exported JSON carries the plan, queries, provider state, errors, all source metadata and fetched text, evidence offsets, candidate claims, candidate conflicts, final cited excerpts, and audit. The database is local to `%LOCALAPPDATA%\Vajra` on Windows, `$XDG`-like user data (`~/.local/share/vajra`) elsewhere, or `VAJRA_DATA_DIR` when set.

Search snippets only identify URLs. They are not stored as evidence. Fetch rechecks the URL, follows a bounded number of validated redirects, limits body size and time, and extracts HTML text without executing JavaScript. Evidence spans are exact character offsets into normalized extracted text. The audit checks the offsets and link graph. Publisher reliability, authorship, source independence, and factual truth are not decided by the current implementation.

For detailed tradeoffs and research citations see [ARCHITECTURE_DECISION.md](ARCHITECTURE_DECISION.md). The upstream capability map is [AGENT_REACH_COMPATIBILITY.md](AGENT_REACH_COMPATIBILITY.md).

