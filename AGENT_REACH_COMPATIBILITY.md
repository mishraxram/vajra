# Agent Reach compatibility matrix

## Observed upstream

- Repository: [Panniantong/Agent-Reach](https://github.com/Panniantong/Agent-Reach)
- Observed current main commit: [`a19a171fa980a0785849596492e0af4db800c82f`](https://github.com/Panniantong/Agent-Reach/commit/a19a171fa980a0785849596492e0af4db800c82f) (2026-09-16; later than release tag)
- Latest published release observed: [v1.5.0](https://github.com/Panniantong/Agent-Reach/releases/tag/v1.5.0), MIT, Python >=3.10
- Locally installed: Agent Reach v1.5.0. Local doctor: 16 channels reported; 5 `ok`, 5 `warn`, 6 `off` (states are environment-specific and can change).
- Source paths below resolve against the observed commit: [`agent_reach/channels/`](https://github.com/Panniantong/Agent-Reach/tree/a19a171fa980a0785849596492e0af4db800c82f/agent_reach/channels), [`doctor.py`](https://github.com/Panniantong/Agent-Reach/blob/a19a171fa980a0785849596492e0af4db800c82f/agent_reach/doctor.py), [`cli.py`](https://github.com/Panniantong/Agent-Reach/blob/a19a171fa980a0785849596492e0af4db800c82f/agent_reach/cli.py), [`integrations/mcp_server.py`](https://github.com/Panniantong/Agent-Reach/blob/a19a171fa980a0785849596492e0af4db800c82f/agent_reach/integrations/mcp_server.py).

This registry is discovered at runtime from `agent-reach doctor --json`; the table records the current upstream capability set and is a review snapshot, not a hard-coded runtime allowlist. Backend order/fallback can vary with upstream version, configuration, and environment. Doctor health does not always prove login or remote service connectivity.

| Capability | Upstream channel | Dependencies / primary backend | Fallbacks (upstream order where defined) | Configuration / health | Vajra access | Test status |
|---|---|---|---|---|---|---|
| GitHub repositories/code | `github.py` | `gh` CLI | No general fallback listed | GitHub CLI auth; doctor status | Dynamic status, backend names, tier | Parity adapter test; CLI access remains upstream |
| Twitter/X posts | `twitter.py` | `twitter-cli` | OpenCLI; legacy `bird` | CLI/login/config; doctor probes backend | Dynamic status only | Parity adapter test; not content wrapped |
| YouTube video/subtitles | `youtube.py` | `yt-dlp` | none reported | `yt-dlp` health | Dynamic status only | Parity adapter test; source tool stays upstream |
| Reddit posts/comments | `reddit.py` | OpenCLI (desktop/login) | `rdt-cli` (login) | Login required; doctor does not prove account access | Dynamic status only | Parity adapter test; login needed |
| Facebook pages/groups/posts | `facebook.py` | OpenCLI + logged-in browser | none reported | Chrome session/daemon; doctor health | Dynamic status only | Parity adapter test; login needed |
| Instagram profile/posts | `instagram.py` | OpenCLI + logged-in browser | none reported | Chrome session/daemon; doctor health | Dynamic status only | Parity adapter test; login needed |
| Bilibili videos/subtitles/search | `bilibili.py` | `bili-cli` | OpenCLI; public Bilibili search API | Doctor may report search-only `ok`; full access differs | Dynamic status only | Parity adapter test; status interpreted as upstream-reported |
| Xiaohongshu notes | `xiaohongshu.py` | OpenCLI (desktop/login) | `xiaohongshu-mcp`; `xhs-cli` | Login/cookies; doctor availability | Dynamic status only | Parity adapter test; login needed |
| LinkedIn career/social | `linkedin.py` | `mcp-server-linkedin` | Jina Reader | mcporter/MCP config and authentication; health not always remote-verified | Dynamic status only | Parity adapter test; MCP source calls stay upstream |
| Boss Zhipin jobs | `boss.py` | `boss-agent-cli` CDP | none reported | Explicit install and user browser login | Dynamic status only | Parity adapter test; not installed here |
| Xiaoyuzhou podcast transcripts | `xiaoyuzhou.py` | Groq/OpenAI Whisper route | ffmpeg transcode | Provider credentials + ffmpeg | Dynamic status only | Parity adapter test; credentials not configured here |
| V2EX topics/replies | `v2ex.py` | Public V2EX API | none reported | Public endpoint health | Dynamic status only | Parity adapter test |
| Xueqiu market/community | `xueqiu.py` | Xueqiu API + login cookie | none reported | User cookie/browser configuration; HTTP errors visible | Dynamic status only | Parity adapter test; local doctor reports warning |
| RSS/Atom feeds | `rss.py` | `feedparser` | none reported | Package availability | Dynamic status only | Parity adapter test; generic feed fetch not wrapped |
| Exa semantic web search | `exa_search.py` | Exa via `mcporter` | none reported | Local mcporter configuration; doctor does not connect-test remote MCP | Status/capability only; not used by Vajra's default no-key research route | Optional upstream capability |
| Arbitrary web pages | `web.py` | Jina Reader | none reported | Public Jina Reader route | AI clients can pass Jina-retrieved text through Vajra MCP or `--sources-file`; Vajra also direct-fetches public pages | Imported exact spans are audited; upstream fetch event is not independently verified |

## Preserved boundary

Vajra does not vendor or modify Agent Reach. It invokes fixed read-only `agent-reach doctor --json` and `agent-reach version` commands with `shell=False`, bounded timeouts, and dynamic JSON parsing. Its default internet research uses DDGS free public search engines and does not call Exa or require credentials. Platform CLI tools, configuration, cookies, installation, update checking, and skill routing remain under Agent Reach and its generated skill. No Agent Reach configuration or user credentials are copied into Vajra. Other platform-specific tools can supply retrieved text to Vajra's evidence pipeline, with explicit attribution and a local content hash; they are never claimed to be independently fetched by Vajra.

## Parity test contract

When Agent Reach is installed, the integration test compares every registry key, status, backend list, active backend, and tier returned by the upstream JSON doctor with the Vajra adapter output. It deliberately does not expect a fixed count or channel list. If Agent Reach is absent, the adapter reports `unavailable` and tests mark the parity check skipped, not passed. The installed-version result and test run are recorded in the final audit.
