# Provider guide

## Search

The default federated provider calls Agent Reach's configured Exa MCP search through `mcporter` and DDGS for each query, deduplicates the returned URLs, then direct-fetches candidate pages. DDGS is pinned to 9.16.0 and tries `auto`, DuckDuckGo, Bing, and Brave. Exa is optional: if mcporter, the Exa server, or network access fails, DDGS still runs. Every backend attempt is recorded. `doctor` checks local package/configuration presence but does not prove live search; only a research run validates connectivity. Search highlights are leads, not evidence: citations are created only from fetched pages or explicitly attributed text passed in by a platform tool.

Agent Reach owns platform-specific channel setup and tools. A compatible AI agent can pass their exact retrieved text to Vajra through MCP `sources_json` or CLI `--sources-file`. Imported items must include the original URL and provider/channel. Vajra hashes and audits the supplied text but cannot independently confirm the external tool's retrieval event. Login-only platforms remain opt-in and follow Agent Reach's own skill/retry guidance.

## Fetch and extract

Direct HTTP fetch accepts HTML, XHTML, XML, and plain text. It validates public network addressing, follows up to five redirects with revalidation, caps each response at 5 MiB and 15 seconds, and does not run JavaScript. Search snippets are not treated as evidence. Extraction records normalized visible text and its SHA-256 content hash. PDF and browser automation adapters are not implemented.

## Agent Reach

Agent Reach is a separate capability/health provider. It dynamically surfaces upstream channel/backends, but content retrieval remains through the upstream channel's own supported tool. Vajra doesn't call arbitrary Agent Reach commands or change Agent Reach configuration. See [AGENT_REACH_COMPATIBILITY.md](AGENT_REACH_COMPATIBILITY.md).
