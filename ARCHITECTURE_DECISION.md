# Architecture decision record

**Status:** accepted for the 0.1 local-first foundation; revisit when an independently measured retrieval/claim-evaluation set exists.

## Problem and requirements

Vajra should run in coding-agent environments, preserve the installed Agent Reach capability layer, collect source-backed passages, expose failures, and replay research runs. It must distinguish search discovery from source retrieval and distinguish text-in-source checks from factual truth. It should run without a model key or paid API by default, keep data local, and avoid broad shell/filesystem tools.

## Research findings

- Agent Reach upstream (MIT, Python 3.10+) is a capability registry, platform installer/configuration/health system, and skill; it routes ordered channel backends and reports dynamic channel status. It is explicitly not a unified read/search API. Its MCP server currently exposes only `get_status`; source-specific reading is done through the selected upstream CLI/API/MCP. Current registry at commit `a19a171fa980a0785849596492e0af4db800c82f` lists 16 channels. The official release page lists v1.5.0; this observed main commit is later than the release tag. [Repository](https://github.com/Panniantong/Agent-Reach), [channels registry at observed commit](https://github.com/Panniantong/Agent-Reach/blob/a19a171fa980a0785849596492e0af4db800c82f/agent_reach/channels/__init__.py), [MCP server](https://github.com/Panniantong/Agent-Reach/blob/a19a171fa980a0785849596492e0af4db800c82f/agent_reach/integrations/mcp_server.py), [releases](https://github.com/Panniantong/Agent-Reach/releases).
- GPT Researcher offers a larger planner/worker/crawler/report framework, but adding the entire runtime would increase model/provider coupling. Its repository `LICENSE` says Apache-2.0 while its current `pyproject.toml` metadata says MIT; Vajra does not reuse its code. [Repository](https://github.com/assafelovic/gpt-researcher), [project metadata](https://github.com/assafelovic/gpt-researcher/blob/main/pyproject.toml), [license](https://github.com/assafelovic/gpt-researcher/blob/main/LICENSE).
- STORM/Co-STORM contributes perspective-guided questions and staged research/outline/writing, but is a research-oriented knowledge-curation framework and not a generic source provider. We adopt the staged research idea, not its runtime. [README](https://github.com/stanford-oval/storm/blob/main/README.md), [package/license metadata](https://github.com/stanford-oval/storm/blob/main/setup.py).
- DDGS provides a small MIT-licensed, Python 3.10+ metasearch library with several backends. It is a discovery adapter whose coverage and availability can change, not an evidence authority. Vajra pins 9.16.0. [Repository](https://github.com/deedy5/ddgs), [license](https://github.com/deedy5/ddgs/blob/main/LICENSE.md), [9.16.0 release metadata](https://pypi.org/project/ddgs/9.16.0/).
- Exa and Tavily combine search with optional extracted text or generated summaries; Firecrawl focuses on crawling/extraction and offers search. Hosted use adds credentials, cost, and service dependency. Firecrawl's main server is AGPL-3.0. Vajra does not integrate these services in 0.1. [Exa search](https://exa.ai/docs/reference/search), [Tavily search](https://docs.tavily.com/documentation/api-reference/endpoint/search), [Tavily extract](https://docs.tavily.com/documentation/api-reference/endpoint/extract), [Firecrawl search](https://docs.firecrawl.dev/features/search), [Firecrawl repository/license](https://github.com/firecrawl/firecrawl).
- MCP's official Python SDK supports local stdio and Streamable HTTP. For a local agent companion, stdio avoids opening a network listener. Version 2.2.0 includes fixes for recent HTTP/OAuth/client redirect advisories; Vajra pins it and does not use HTTP/OAuth. [SDK run/transport docs](https://py.sdk.modelcontextprotocol.io/run/), [v2.2.0 release](https://github.com/modelcontextprotocol/python-sdk/releases/tag/v2.2.0), [security advisories](https://github.com/modelcontextprotocol/python-sdk/security/advisories).

## Candidates and tradeoffs

| Candidate | Benefit | Cost/risk | Decision |
|---|---|---|---|
| Depend directly on a full research agent | Fast broad feature surface | Model/API and orchestration lock-in; larger security and license surface; hard to audit evidence guarantees | Rejected for the core |
| Vendor Agent Reach | Offline source access | Fork/upgrade divergence; platform tools still external; unnecessary MIT code duplication | Rejected |
| Use Agent Reach as a provider | Preserves platform setup and routing | Upstream status MCP does not provide general page/search content | Use as a dynamic capability/health adapter, retain native upstream CLI and skill access |
| Local SQLite + explicit search/fetch/evidence layers | Inspectable, replayable, no server or model key required | Local filesystem; HTML extraction and claim semantics are limited | Selected |
| Hosted Exa/Tavily/Firecrawl | Higher quality or richer extraction options | API keys, usage cost, third-party processing, varying contracts | Deferred behind future provider adapters |
| MCP over local stdio | Agent interoperability without a listening socket | Trust still rests on the launched local process; an agent can request network research | Selected; narrow typed tools only |

## Final architecture

Python 3.10+ package, stdlib CLI/logging/SQLite and data models, optional pinned DDGS search, bounded `urllib` HTML/text fetching with public-address checks, exact source passages, SQLite run ledger, deterministic JSON/Markdown export, and a pinned official MCP Python SDK v2 stdio adapter. Provider interfaces separate search and Agent Reach health. Source text is stored with retrieval time and SHA-256; evidence records store exact offsets. Candidate claims are verbatim passages and start at `PARTIALLY_VERIFIED`; this status only means source text was captured, not that it is true.

The 0.1 research plan is deterministic query expansion, bounded search/fetch, lexical passage ranking, and (in deep modes) a separately worded counterevidence query plus a conservative polarity-overlap candidate flag. It does not use an LLM, entailment classifier, or semantic contradiction judge. No output prose is generated as a factual claim except verbatim attributed passages and fixed audit language.

## Security, performance, cost, maintenance

- Search is optional and unauthenticated through the pinned DDGS library; providers may rate-limit, change, or fail. Search health means importable, not network-tested.
- Fetch accepts HTTP(S), rejects credentials/private/non-global DNS results, revalidates redirects, caps redirect count, bytes, and timeout, and does not execute scripts. DNS can still change between validation and connection (rebinding/TOCTOU); see the threat model. JavaScript-only and PDF sources are unsupported in 0.1.
- MCP is local stdio only. Tool calls do not expose arbitrary shell, path, or browser-cookie operations. Logs go to stderr. Research MCP calls can access public websites, so hosts must treat tool choice as a network side effect.
- SQLite uses local app data and transactions; no embeddings/vector DB are justified before measured retrieval needs. No costs are incurred by Vajra itself; network availability, terms, and rate limits depend on DDGS/search backends and websites.
- Concurrency is capped at four fetch workers and each source is capped at 5 MiB. No performance claim is made until benchmark data is collected.

## Rejected alternatives and reassessment triggers

We do not reuse full GPT Researcher, STORM, LangChain Open Deep Research, Firecrawl, Exa, or Tavily runtimes in the core. Their design patterns informed the provider/orchestration boundaries; their dependencies, billing, licensing, operational model, or research-project scope do not justify adoption yet. Reassess after labeled tasks demonstrate a gap that an external dependency closes, after adding JS/PDF support, or before exposing network MCP over HTTP.

