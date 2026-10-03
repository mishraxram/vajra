# Release audit

**Decision: NOT READY / NOT RELEASED.** This is an initial, usable research-workbench build. The evidence below records what ran on 2026-10-03 and keeps unresolved release criteria visible. Do not describe this build as production-ready.

## Verified

| Area | Status | Evidence |
|---|---|---|
| Environment/project discovery | PASS | Windows 11, Python 3.13.15, Node 24.19, git 2.55, WSL 3.0.1; 16 GB RAM; empty projectless workspace. No Docker and GitHub CLI is unauthenticated. Existing Agent Reach was preserved. |
| Ecosystem and architecture research | PASS, scoped | Primary-source review recorded in architecture/provider documents; candidates include Agent Reach, STORM, GPT Researcher, DDGS, MCP SDK, and alternatives. Research is not an exhaustive survey of every candidate. |
| Agent Reach preservation/parity | PASS for adapter boundary | Installed v1.5.0; current main commit `a19a171fa980a0785849596492e0af4db800c82f`; its 16 channel keys and status/backend/tier data are read dynamically. Parity test passed. Doctor reported 5/16 channels healthy in this environment. Agent Reach is a capability/health integration here, not a generic retrieval API. |
| Upstream update check | PASS | `vajra upstream-check` completed read-only and reported installed v1.5.0 is current on 2026-10-03. No update was installed. |
| Package/lock | PASS | `uv lock --check` resolved 36 packages without lock drift. `uv build` successfully produced wheel and sdist. Fresh isolated `uv sync --all-extras --frozen` installed successfully and `vajra --version` returned 0.1.0. |
| Tests | PASS, limited | 10 tests passed in the existing environment and again in a fresh locked environment. Includes Agent Reach parity, evidence replay/audit, fetch validation, security checks, and real MCP stdio client calls. This is not comprehensive production qualification. |
| MCP | PASS, stdio only | SDK 2.2.0; subprocess test connected with the official client and exercised tools. No network transport or third-party agent configuration was changed. |
| CLI/doctor | PASS, limited | Doctor ran and reported `AVAILABLE`; database and optional dependencies were configured. Search network is explicitly `not probed`; 5/16 Agent Reach channels were healthy. Doctor does not assert test status or claim truth verification. |
| Live research smoke | PASS, limited | DDGS search and direct fetch produced a trace with fetched sources/passages; citation audit reported valid. Provider behavior varied and some metasearch backends throttled/failed. This is one smoke workflow, not evidence of broad research quality. |
| Dependency vulnerability scan | PASS, scoped | `pip-audit` scanned all locked optional runtime dependencies exported without the local project and reported “No known vulnerabilities found.” Scan date: 2026-10-03. Vulnerability databases and transitive platform selection can change. |
| Third-party license inventory | PASS, scoped | Direct components were reviewed; `pip-licenses` inventoried the resolved Windows CPython 3.13 environment. See `THIRD_PARTY_NOTICES.md`; lockfile includes platform-conditional dependencies. |
| Git | PASS | Initialized a local repository and created an initial project commit. No remote was configured. GitHub CLI has no authenticated account, so no remote release/PR was attempted. |

## Not passed / not run

| Area | Status | Remaining work |
|---|---|---|
| Full research intelligence | NOT IMPLEMENTED | No semantic claim extraction, entailment, source authority scoring, independent-source adjudication, temporal validity judgment, general contradiction resolution, or final evidence-based judgment. Current “claims” are source excerpts. |
| Provider routing/fallback | PARTIAL | DDGS search plus direct HTTP retrieval work; Agent Reach health is preserved. There is no capability-based multi-provider content router or functioning alternate content provider fallback. |
| Comparative benchmark | NOT RUN | No fair Agent Reach-vs-Vajra full-workflow benchmark was run. Agent Reach exposes capability-specific integrations and health checks, not a comparable generic report-generation workflow. Do not infer quality, coverage, or superiority. |
| Performance/resource benchmarks | NOT RUN | No reproducible end-to-end latency, CPU, memory, network, cache, cost, throughput, or failure-recovery study. |
| Broad adversarial security audit | PARTIAL | Unit/security tests cover selected URLs, spans, and MCP boundaries. No independent penetration test, fuzzing, complete prompt-injection campaign, DNS-rebinding defense, or sandboxing review. URL validation checks resolved addresses but retains a DNS time-of-check/time-of-use risk. |
| Cross-platform clean install | NOT RUN | Fresh install was verified on Windows CPython 3.13 only; Linux/macOS CI was not executed. |
| Release distribution | NOT RELEASED | No signed artifact, PyPI publication, GitHub release, remote repository, or release pipeline run. GitHub authentication is unavailable. |

## Release gate

Keep the release blocked until the missing research-verification and provider-routing capabilities are either implemented or explicitly removed from the product goal; a versioned human-adjudicated benchmark is run; performance and adversarial security results are measured; cross-platform installation is checked; and release artifacts receive a fresh review. The current local build is suitable for continued development and cautious experimentation, not a production-readiness claim.
