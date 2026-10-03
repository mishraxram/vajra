# Install VAJRA

Use Python 3.10 or newer. VAJRA installs into the user's `uv` tool environment; it does not install browser extensions, alter shell profiles, or configure an AI client for you.

## CLI and MCP server

If `uv` is not installed yet, install it once with `python -m pip install uv`. Then:

```powershell
uv tool install git+https://github.com/mishraxram/vajra.git
vajra --version
vajra doctor
```

The command installs the `vajra` executable plus its search and MCP runtime dependencies. Restart the terminal if the command is not found after installation.

## Reusable skill for supported coding agents

The public Agent Skills installer can install VAJRA's `SKILL.md` into the global skill locations of supported clients, including OpenCode, Codex, Claude Code, Cursor, and GitHub Copilot CLI:

```powershell
npx skills add mishraxram/vajra --skill vajra-research --global --yes --agent '*'
```

This installs the skill instructions. It does not install VAJRA's executable; run the `uv tool install` command above for the working CLI/MCP tools. Remove `--global` to install the skill into the current project instead.

## Connect MCP clients

Follow the short client-specific commands and config examples in [AGENT_INTEGRATIONS.md](AGENT_INTEGRATIONS.md). A client needs to support local stdio MCP to use VAJRA's actual tools. A skill-compatible client can still follow the CLI workflow without MCP.

## One-message setup for an AI agent

Send this to an AI coding agent with terminal access:

> Install VAJRA for me using the steps at https://raw.githubusercontent.com/mishraxram/vajra/master/INSTALL.md. Install the CLI and global skill, verify `vajra --version`, then show me the MCP setup for my current client. Do not claim a client is connected until its MCP status confirms it.

Installation grants the local VAJRA process the ability to perform public web searches when its research command or MCP tool is explicitly invoked. Review the repository's [security notes](SECURITY.md) and [limitations](README.md#current-limits).
