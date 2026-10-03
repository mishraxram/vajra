# Security policy

Vajra processes attacker-controlled search results and website content. Do not treat retrieved content, citations, or MCP metadata as instructions. Report vulnerabilities privately through the repository owner's configured security channel once one exists; this standalone initial project has no public advisory endpoint.

## Implemented controls

- URL scheme, host, userinfo, private/reserved IP, and redirect validation; request timeout, redirect cap, and 5 MiB response limit.
- HTML script/style/form/iframe content is omitted and never executed. Unsupported response types fail visibly.
- MCP runs over local stdio only; its tools expose research/replay/audit/Agent Reach status, not shell or arbitrary file reads/writes.
- SQLite parameterized queries, internally generated 128-bit run IDs, bounded search/fetch fanout, and exact citation span auditing.
- Optional dependency versions are pinned. No secrets are required by default; local Agent Reach auth is not copied into reports.

## Known security gaps

- DNS is checked before the HTTP library resolves/connects, leaving a DNS rebinding/time-of-check-to-time-of-use gap. Do not use Vajra as an exposed URL-fetch service or in a hostile network until socket-level address pinning is implemented and audited.
- Standard-library HTML extraction is conservative but not a full hostile-document sanitizer; text remains untrusted. PDFs, archives, and JavaScript execution are unsupported.
- SQLite files and reports contain fetched source text and should be protected by the user's OS account permissions and backup policy.
- Search backend implementations are third-party and can change; pinned package provenance and dependency scanning need a release pipeline.
- Windows filesystem ACLs are inherited from the selected data directory; Vajra does not alter ACLs.

See [THREAT_MODEL.md](THREAT_MODEL.md) for trust boundaries and mitigations.

