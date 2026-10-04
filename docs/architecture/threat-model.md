# Stabilization threat-model snapshot

This is a Phase 0 inventory of existing boundaries, not a new security design.
The repository's [`THREAT_MODEL.md`](../../THREAT_MODEL.md) remains the fuller
product threat model.

| Boundary | Existing control observed | Residual risk relevant to stabilization |
|---|---|---|
| Network URLs and redirects | HTTP(S) only, public DNS/IP validation, redirect revalidation, response bounds | DNS can change between validation and connection; library behavior remains relevant |
| Fetched content | No script execution; HTML clutter/hidden content removed; text labeled untrusted | A host model can still mis-handle quoted instructions |
| Agent Reach subprocess | Fixed command/argument lists, `shell=False`, bounded timeouts, sanitized status output | Executable and upstream output are external; test malformed and failing processes |
| Browser sessions and account credentials | Vajra does not read browser cookies or copy Agent Reach credentials; Agent Reach owns its configured sessions | Agent Reach and its upstream tools have their own account/session risks |
| MCP | Local stdio server, declared tools, bounded input payloads | Host process permissions and requested network activity are inherited |
| Persistence | Local SQLite under user data directory or explicit override | No explicit restrictive file permissions, encryption, or retention controls |
| Build and dependencies | Exact runtime pins and committed uv lock; setuptools build requirement pinned | No existing lint/type/coverage gates or installed-wheel smoke in CI |

Phase 1 adds verification of these existing paths. It does not introduce browser
automation, cookie access, CAPTCHA handling, or new subprocess capabilities.
