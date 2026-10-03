# Provider guide

## Search

The `SearchProvider` protocol has a required DDGS adapter pinned to 9.16.0. For each query it tries DDGS `auto`, then the DuckDuckGo, Bing, and Brave backends until one returns results. It records each attempt in the trace. `doctor` reports whether the package imports; it does not issue a network probe. Search results provide candidate URLs and snippets only. A search error is stored with its query and provider; an empty/failed search does not generate a citation.

Exa, Tavily, and Firecrawl were reviewed but are not enabled in the initial release. Adding them should require separate adapters, explicit key handling, cost metadata, and tests that keep vendor-generated answers separate from fetched evidence.

## Fetch and extract

Direct HTTP fetch accepts HTML, XHTML, XML, and plain text. It validates public network addressing, follows up to five redirects with revalidation, caps each response at 5 MiB and 15 seconds, and does not run JavaScript. Search snippets are not treated as evidence. Extraction records normalized visible text and its SHA-256 content hash. PDF and browser automation adapters are not implemented.

## Agent Reach

Agent Reach is a separate capability/health provider. It dynamically surfaces upstream channel/backends, but content retrieval remains through the upstream channel's own supported tool. Vajra doesn't call arbitrary Agent Reach commands or change Agent Reach configuration. See [AGENT_REACH_COMPATIBILITY.md](AGENT_REACH_COMPATIBILITY.md).
