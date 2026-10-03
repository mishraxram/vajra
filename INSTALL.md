# Install VAJRA

Use Python 3.10 or newer. VAJRA installs into the user's `uv` tool environment; it does not install browser extensions, alter shell profiles, or configure an AI client for you.

Core web research is free and keyless: it uses public DDGS search backends and does not need an API key, paid plan, or login. Optional platform skills may have their own upstream requirements, but they are not needed for Vajra's default web research.

## CLI and MCP server

If `uv` is not installed yet, install it once with `python -m pip install uv`. Then:

```powershell
uv tool install --from git+https://github.com/mishraxram/vajra.git vajra-research
if ($LASTEXITCODE -eq 0) {
  $env:PATH = "$(uv tool dir --bin);$env:PATH"
  vajra welcome
}
vajra --version
```

This installs the `vajra` executable plus its search and MCP runtime dependencies, adds the uv executable directory to this PowerShell session, then runs the branded welcome check. In an interactive terminal `vajra welcome` prompts for a research question; in a non-interactive agent terminal it displays the banner and exits cleanly. Restart the terminal if `vajra` is not found in later sessions.

Run `vajra doctor` only when `vajra welcome` reports a setup problem or you need its full diagnostics; doctor also checks the optional Agent Reach integration and may take longer.

## Reusable skill for supported coding agents

The public Agent Skills installer can install VAJRA's `SKILL.md` into the global skill locations of supported clients, including OpenCode, Codex, Claude Code, Cursor, and GitHub Copilot CLI:

```powershell
npx skills add mishraxram/vajra --skill vajra-research --global --yes --agent '*'
```

This installs the skill instructions. It does not install VAJRA's executable; run the `uv tool install` command above for the working CLI/MCP tools. Remove `--global` to install the skill into the current project instead.

## Connect MCP clients

Follow the short client-specific commands and config examples in [AGENT_INTEGRATIONS.md](AGENT_INTEGRATIONS.md). A client needs to support local stdio MCP to use VAJRA's actual tools. A skill-compatible client can still follow the CLI workflow without MCP.

## One-message setup for an AI agent

For any AI CLI with terminal access and Agent Skills support, send:

> Set up VAJRA on this machine: detect my OS, install `uv` only if missing, install the CLI and global skill for supported AI CLIs, verify both, and configure this client's documented MCP setup if supported. Don't ask follow-up questions; reply only with a concise success or the exact blocker.

The Agent Skills installer targets the clients it supports; no installer can configure every AI CLI. Client-specific MCP steps are listed in [AGENT_INTEGRATIONS.md](AGENT_INTEGRATIONS.md). Do not claim MCP is connected until that client confirms it.

Installation grants the local VAJRA process the ability to perform public web searches when its research command or MCP tool is explicitly invoked. Review the repository's [security notes](SECURITY.md) and [limitations](README.md#current-limits).
