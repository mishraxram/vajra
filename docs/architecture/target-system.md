# Phase 1 target and non-goals

This target is deliberately limited to release stabilization.

## Target modules and dependency direction

- Keep `cli.py` and `mcp_server.py` as the existing public interfaces.
- Keep the existing provider protocols and engine; make provider health
  results total and test their CLI-facing diagnostic handling.
- Keep `store.py` as persistence and existing URL validation/fetch boundaries.
- Add tests that install the built wheel into an isolated environment and call
  the public CLI and MCP tool-listing surface without `PYTHONPATH` adjustments.
- Keep the runtime dependency set unchanged. Add pinned development tools for
  pytest, coverage, Ruff, and production-source type checking in the lockfile.

## Contracts exercised by Phase 1

- Search provider health always returns `(status, message)` strings; missing
  `ddgs` is `unavailable`, and an importable provider is `configured` without
  claiming network connectivity.
- `vajra doctor` emits a JSON object with `overall` and named `checks` fields.
- The installed MCP server lists `vajra_research`, `vajra_replay`,
  `vajra_audit`, and `agent_reach_status` over stdio.
- Agent Reach remains a dynamic health report sourced from
  `agent-reach doctor --json`; no content-operation result is implied.

## Migration sequence

1. Record pre-change test, doctor, lint/type/coverage, and smoke baseline.
2. Fix the DDGS health tuple and add direct tests for health and Agent Reach
   subprocess outcomes.
3. Add reproducible isolated wheel/CLI/MCP smoke coverage; correct packaging
   issues revealed by it.
4. Add CI gates for unittest, pytest, coverage, Ruff, type checking, clean wheel
   build/install, and smoke tests.
5. Re-run all gates and update user documentation only for observed behavior.

## Explicit non-goals

No connectors, new research backends, capability registry, routing redesign,
storage migration, security redesign, or engine rewrite. Later phases in the
master prompt are out of scope for this session.
