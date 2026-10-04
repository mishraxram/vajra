# Agent Reach compatibility baseline

The runtime boundary and observed channel/back-end snapshot are documented in
the repository's [Agent Reach compatibility matrix](../../AGENT_REACH_COMPATIBILITY.md).
That matrix records a review snapshot, not a hard-coded runtime capability
list. The adapter parses `agent-reach doctor --json` dynamically and exposes
health metadata only; it does not invoke platform content operations.

The repository's `agent-reach-upstream.json` identifies the inspected upstream
revision and release. The checked-in skill at
`.agents/skills/vajra-research/SKILL.md` describes separate Agent Reach tools
and client-side MCP configuration. Local parity is covered by
`tests/test_agent_reach_parity.py` when the executable is present. The Phase 1
stabilization will add deterministic fake-executable tests for absent,
well-formed, malformed, timed-out, and non-zero doctor invocations. No upstream
connector or Agent Reach execution adapter is introduced in this session.

For Phase 0 source verification, the upstream v1.5.0 tag was checked out at
`f65526cbaaad3879473acc1ba6dbefd195caf2be`. Its package declares a Hatchling
wheel build and Python 3.10 support. The source tree has a channel base class,
per-channel health probes, a shared subprocess probe helper, skill references,
and an optional single-tool MCP status server. `agent_reach doctor` collects
channel health and active backend metadata; the MCP server exposes
`get_status`. The skill/install guide directs agents to call upstream CLIs,
MCPs, and APIs for content operations. The upstream package includes
configuration and cookie/session helpers, and its docs describe authenticated
channels; these credentials and capabilities stay outside Vajra's adapter.
The checkout contained per-channel and helper tests for doctor, subprocess
classification, configuration, CLI, cookies, formatting, and platform behavior.
