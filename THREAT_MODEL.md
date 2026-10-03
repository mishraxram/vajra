# Threat model

## Assets and boundaries

Assets: local reports, evidence database, Agent Reach installation/configuration/cookies, shell and environment credentials. Untrusted inputs: search results, URLs, redirects, HTML, metadata, and external text. Trust boundary: the Vajra Python process and the MCP host that launches it. Vajra should not be granted broad filesystem/shell access by a host.

## Threats

| Threat | Control in 0.1 | Residual risk |
|---|---|---|
| Prompt injection in page text | Content is stored and quoted only as data; no model is run over it by the core; MCP instructions explicitly call it untrusted | A host model may still act on quoted malicious text; host policy matters |
| SSRF and redirects | Only HTTP(S); block URL credentials, local names/private/non-global DNS answers; each redirect revalidated; finite redirects/body/time | DNS rebinding between validation and socket connect remains; do not expose as network service |
| Malicious content/large documents | No JS, file execution, or PDF parsing; size and type caps | HTML parser edge cases and resource exhaustion remain possible within caps |
| Secret exfiltration | No secrets required; no arbitrary shell tools; Agent Reach config never copied; logs avoid source content | MCP host controls process environment; upstream CLIs may access their own configured credentials |
| Path traversal | Run IDs are internal hex values and validated before report path creation; data dir is operator-selected | Local user still controls data dir and can modify files |
| Citation fabrication | Citations derive from fetched source records; quote offsets and IDs are audited; failures stored | Publisher truth, relevance, freshness, and quote context are not proven by string matching |
| Denial of service/cost | Bounded query count, fetch count, concurrency, timeouts, and bytes; no paid provider by default | Third-party search endpoints can block/rate-limit; MCP caller can request repeated work |
| Supply-chain compromise | Exact direct dependency pins; third-party notices and sources recorded | No automated vulnerability scanner/SBOM pipeline yet |

## MCP trust

The local stdio server has the permissions of its host process. It does not listen on a network port and does not expose a generic fetch URL or shell command. `vajra_research` can initiate public network traffic. Hosts should review tool descriptions and obtain user approval according to their own interaction policy before invoking potentially expensive or externally visible actions. Agent Reach's separate tools can carry account/session state; those remain governed by Agent Reach and the MCP server that owns them.

