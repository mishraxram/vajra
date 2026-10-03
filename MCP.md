# MCP integration

Vajra provides an optional local stdio MCP server based on the official Python SDK 2.2.0. Local stdio was selected because the host launches a subprocess and there is no HTTP listener, remote auth endpoint, CORS, or network session to secure. The official SDK documents stdio as the local transport and Streamable HTTP for deployment; legacy SSE is not selected. [SDK transport docs](https://py.sdk.modelcontextprotocol.io/run/), [SDK release](https://github.com/modelcontextprotocol/python-sdk/releases/tag/v2.2.0).

Install with `python -m pip install -e ".[mcp]"`, then configure the MCP host to launch the installed `vajra mcp` command. Tools: `vajra_research(question, mode)`, `vajra_replay(research_id)`, `vajra_audit(research_id)`, and `agent_reach_status()`. There is no arbitrary shell, local-file, cookie, or URL-fetch tool. The research tool does perform bounded public search/fetch when called.

All tools return source text/metadata as untrusted research data. Stdout is reserved for MCP framing; ordinary logs go to stderr. The SDK is pinned to 2.2.0, the patched release observed after September/October 2026 advisories. Vajra does not use MCP's HTTP client or authorization features. Always review security advisories before upgrading. [SDK advisories](https://github.com/modelcontextprotocol/python-sdk/security/advisories).

