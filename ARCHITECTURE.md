# Architecture

```text
CLI / local MCP stdio
         |
Research planner -> asyncio bounded worker pools
    |                         |
Federated search         bounded public fetches
Exa -> DDGS route         URL/redirect/size/deadline checks
    |                         |
AgentReach health       semantic HTML/text extraction
    |                         |
untrusted text boundary + token-budgeted replay chunks
              |
Exact passage evidence + candidate claims + citation audit
              |
SQLite run ledger -> research.json + Markdown report
```

`async_run_research` is the async entry point. Synchronous search and urllib
providers run in bounded worker threads because those upstream APIs are
synchronous; an asyncio semaphore caps parallel tasks, and provider/network
timeouts cap their work. The CLI and MCP wrapper call the synchronous `run_research`
entry point. Fetch extraction preserves headings, lists, and quotations while
drops scripts, styles, hidden elements, navigation, headers, footers, and common
ad clutter. MCP replay omits bulk source bodies by default; request a `source_id`
and `chunk_index` to read exact-offset overlapping chunks (about 4 characters per
estimated token).

Vajra does not spoof browser fingerprints, inject session cookies, automate
account sessions, bypass CAPTCHAs/Cloudflare, or capture challenge screenshots.
401/403/407/429 responses and detected challenge pages are recorded as access
failures. The caller can use a documented/authorized source API or inspect the
page manually. Visible adversarial instructions in web content remain quoted
source data, are never executed, and are marked untrusted; invisible control and
bidirectional formatting characters are removed.

`ResearchStore` is the durable source of replay data. The exported JSON carries the plan, queries, provider state, errors, all source metadata and fetched text, evidence offsets, candidate claims, candidate conflicts, final cited excerpts, and audit. The database is local to `%LOCALAPPDATA%\Vajra` on Windows, `$XDG`-like user data (`~/.local/share/vajra`) elsewhere, or `VAJRA_DATA_DIR` when set.

Search snippets only identify URLs. They are not stored as evidence. Fetch rechecks the URL, follows a bounded number of validated redirects, limits body size and time, and extracts HTML text without executing JavaScript. Evidence spans are exact character offsets into normalized extracted text. The audit checks the offsets and link graph. Publisher reliability, authorship, source independence, and factual truth are not decided by the current implementation.

For detailed tradeoffs and research citations see [ARCHITECTURE_DECISION.md](ARCHITECTURE_DECISION.md). The upstream capability map is [AGENT_REACH_COMPATIBILITY.md](AGENT_REACH_COMPATIBILITY.md).
