# Release audit

**Decision: NOT PRODUCTION-READY / NO PYPI RELEASE.** The source is public on GitHub as an experimental work in progress. Base environment, research, build, and security-scan observations are from 2026-10-03; benchmark-scorer work, final test reruns, and GitHub publication are from 2026-10-04. Unresolved release criteria remain visible. Do not describe this build as production-ready.

## Verified

| Area | Status | Evidence |
|---|---|---|
| Environment/project discovery | PASS | Windows 11, Python 3.13.15, Node 24.19, git 2.55, WSL 3.0.1; 16 GB RAM; empty projectless workspace. No Docker. GitHub CLI was initially unauthenticated; user logged in and authorized public source publication. Existing Agent Reach was preserved. |
| Ecosystem and architecture research | PASS, scoped | Primary-source review recorded in architecture/provider documents; candidates include Agent Reach, STORM, GPT Researcher, DDGS, MCP SDK, and alternatives. Research is not an exhaustive survey of every candidate. |
| Agent Reach preservation/parity | PASS for adapter boundary | Installed v1.5.0; current main commit `a19a171fa980a0785849596492e0af4db800c82f`; its 16 channel keys and status/backend/tier data are read dynamically. Parity test passed. Doctor reported 5/16 channels healthy in this environment. Agent Reach is a capability/health integration here, not a generic retrieval API. |
| Upstream update check | PASS | `vajra upstream-check` completed read-only and reported installed v1.5.0 is current on 2026-10-03. No update was installed. |
| Package/lock | PASS | `uv lock --check` resolved 36 packages without lock drift. `uv build` successfully produced wheel and sdist. Fresh isolated `uv sync --all-extras --frozen` installed successfully and `vajra --version` returned 0.1.0. |
| Tests | PASS, limited | All 13 tests passed in the existing environment and again in a fresh locked environment on 2026-10-04. Includes Agent Reach parity, evidence replay/audit, fetch validation, security checks, benchmark-scorer behavior, and real MCP stdio client calls. This is not comprehensive production qualification. |
| MCP | PASS, stdio only | SDK 2.2.0; subprocess test connected with the official client and exercised tools. No network transport or third-party agent configuration was changed. |
| CLI/doctor | PASS, limited | Doctor ran and reported `AVAILABLE`; database and optional dependencies were configured. Search network is explicitly `not probed`; 5/16 Agent Reach channels were healthy. Doctor does not assert test status or claim truth verification. |
| Live research smoke | PASS, limited | DDGS search and direct fetch produced a trace with fetched sources/passages; citation audit reported valid. Provider behavior varied and some metasearch backends throttled/failed. This is one smoke workflow, not evidence of broad research quality. |
| Dependency vulnerability scan | PASS, scoped | `pip-audit` scanned all locked optional runtime dependencies exported without the local project and reported “No known vulnerabilities found.” Scan date: 2026-10-03. Vulnerability databases and transitive platform selection can change. |
| Third-party license inventory | PASS, scoped | Direct components were reviewed; `pip-licenses` inventoried the resolved Windows CPython 3.13 environment. See `THIRD_PARTY_NOTICES.md`; lockfile includes platform-conditional dependencies. |
| Git | PASS | Public repository [`mishraxram/vajra`](https://github.com/mishraxram/vajra) created on 2026-10-04; local commits pushed to `master`. Public visibility verified through GitHub API. Corrected `uv tool install --from ... vajra-research` command was tested in isolated tool/bin directories: it installed 33 packages and produced `vajra 0.1.0`. |

## Not passed / not run

| Area | Status | Remaining work |
|---|---|---|
| Full research intelligence | NOT IMPLEMENTED | No semantic claim extraction, entailment, source authority scoring, independent-source adjudication, temporal validity judgment, general contradiction resolution, or final evidence-based judgment. Current “claims” are source excerpts. |
| Provider routing/fallback | PARTIAL | DDGS search plus direct HTTP retrieval work; Agent Reach health is preserved. There is no capability-based multi-provider content router or functioning alternate content provider fallback. |
| Benchmark harness | PASS, limited | Deterministic scorer is implemented and unit-tested for exact evidence spans and trace integrity. No quality benchmark has run because no human-adjudicated corpus exists. |
| Comparative benchmark | NOT RUN | No fair Agent Reach-vs-Vajra full-workflow benchmark was run. Agent Reach exposes capability-specific integrations and health checks, not a comparable generic report-generation workflow. Do not infer quality, coverage, or superiority. |
| Performance/resource benchmarks | NOT RUN | No reproducible end-to-end latency, CPU, memory, network, cache, cost, throughput, or failure-recovery study. |
| Broad adversarial security audit | PARTIAL | Unit/security tests cover selected URLs, spans, and MCP boundaries. No independent penetration test, fuzzing, complete prompt-injection campaign, DNS-rebinding defense, or sandboxing review. URL validation checks resolved addresses but retains a DNS time-of-check/time-of-use risk. |
| Cross-platform clean install | NOT RUN | Fresh install was verified on Windows CPython 3.13 only; Linux/macOS CI was not executed. |
| Release distribution | PARTIAL | Public source is available on GitHub. No PyPI package, signed artifact, GitHub tagged release, or release workflow run exists. The project remains explicitly experimental and not production-ready. |

## Release gate

Keep the release blocked until the missing research-verification and provider-routing capabilities are either implemented or explicitly removed from the product goal; a versioned human-adjudicated benchmark is run; performance and adversarial security results are measured; cross-platform installation is checked; and release artifacts receive a fresh review. The current local build is suitable for continued development and cautious experimentation, not a production-readiness claim.

## Installability follow-up: 0.2.0 (2026-10-04)

| Area | Status | Evidence |
|---|---|---|
| One-command GitHub install | PASS | In an isolated Windows tool/bin directory, `uv tool install git+https://github.com/mishraxram/vajra.git` fetched commit `91962709b3c494c313ffeb163538774f4b9fe0ec`, installed 33 packages, and created the `vajra` executable at version 0.2.0. This removes the old `--from ... vajra` distribution-name mismatch. |
| Installed CLI smoke | PASS, limited | The freshly installed executable completed a live `fast` research run with 1 fetched source and 3 exact passages; `vajra audit` returned `valid: true`. Search succeeded through DDGS `auto`. This single query does not establish general coverage or research quality. |
| Local checks/build | PASS, limited | `uv lock --check`; all 17 unit/integration tests; and `uv build` produced the 0.2.0 wheel and source distribution on Windows CPython 3.13. |
| GitHub CI | PASS | Matrix workflow [run 37147381681](https://github.com/mishraxram/vajra/actions/runs/37147381681) passed on commit `91962709b3c494c313ffeb163538774f4b9fe0ec`. |
| GitHub discovery metadata | PASS | Repository description updated and topics added for `ai-agents`, `deep-research`, `evidence`, `mcp`, `open-source`, `python`, and `research`. Discovery metadata cannot guarantee popularity. |
| Doctor interpretation | PASS, limited | Fresh install reported `overall: CONFIGURED`, with database, DDGS, and MCP configured. The separately reported Agent Reach health subprocess timed out; search network remains unprobed by `doctor`. |

This follow-up verifies a convenient experimental GitHub install. It does not change the production-readiness decision above, publish a PyPI package, or qualify the project for consequential use.
