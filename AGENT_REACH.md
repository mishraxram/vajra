# Agent Reach integration

Agent Reach is mandatory as a preserved capability layer. Vajra dynamically calls its read-only JSON doctor and version commands. It does not rewrite its configuration, install platform CLIs, read cookies, claim a channel works when upstream marks it unavailable, or wrap every platform's distinct API into an invented generic API.

To use platform-specific access, install and configure Agent Reach through its [official upstream docs](https://github.com/Panniantong/Agent-Reach/blob/main/docs/install.md), inspect `agent-reach doctor`, and use its generated skill and supported platform-specific tools. Vajra reports those capabilities using their runtime channel names, backend candidates, active backend, tier, and upstream health state.

The locally observed upstream is v1.5.0, with 16 dynamically reported channels, and uses MIT. The compatibility matrix documents the observed main commit and the distinct backend limits. A later upstream update may add/remove/rename capabilities; runtime discovery and parity tests are intended to surface this without a stale Vajra channel registry.

