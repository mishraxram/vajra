# AI agent integrations

VAJRA exposes the same real research workflow in two ways: a CLI and a local stdio MCP server. Agent Skills are reusable instructions that teach a client how to invoke and audit that workflow. On Windows, install the runtime and show the branded welcome screen with the [PowerShell install block in INSTALL.md](INSTALL.md#cli-and-mcp-server). On macOS/Linux/WSL, use the matching install-and-welcome command in the [README](README.md#install-and-run).

To install the skill globally for supported agent clients:

```powershell
npx skills add mishraxram/vajra --skill vajra-research --global --yes --agent '*'
```

The skill installer supports a broad ecosystem, but no single setup format works for every AI client. Use the client's native method below and restart/reload that client after setup.

## OpenCode

OpenCode can load the skill from its shared `.agents/skills` location. Its CLI can register VAJRA globally:

```sh
opencode mcp add vajra --global -- vajra mcp
```

Or add this to `opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "vajra": {
      "type": "local",
      "command": ["vajra", "mcp"],
      "enabled": true
    }
  }
}
```

## Codex CLI

```sh
codex mcp add vajra -- vajra mcp
codex mcp list
```

## Claude Code

```sh
claude mcp add --scope user vajra -- vajra mcp
claude mcp list
```

On native Windows, if the client cannot launch the executable directly, use its documented Windows command wrapper and invoke `vajra.exe mcp` through `cmd /c`.

## VS Code / GitHub Copilot, Cursor, and portable MCP clients

For VS Code's portable workspace format, add this to `.mcp.json` in the workspace root. Cursor uses the same `mcpServers` shape in its MCP configuration; GitHub Copilot CLI also supports a local MCP configuration file.

```json
{
  "mcpServers": {
    "vajra": {
      "command": "vajra",
      "args": ["mcp"]
    }
  }
}
```

VS Code's native `.vscode/mcp.json` format instead uses a top-level `servers` object:

```json
{
  "servers": {
    "vajra": {
      "type": "stdio",
      "command": "vajra",
      "args": ["mcp"]
    }
  }
}
```

## Verify it actually works

```sh
vajra --version
vajra doctor
vajra research "A focused question with evidence on both sides" --mode standard
vajra audit RESEARCH_ID
```

The MCP server exposes `vajra_research`, `vajra_replay`, `vajra_audit`, and `agent_reach_status`. In the client's MCP panel/list, confirm VAJRA is connected and these tools are listed before assuming the integration is active. `doctor` checks local setup; its search network field is explicitly not probed.

## Protocol/source references

- [OpenCode skills](https://opencode.ai/docs/skills) and [OpenCode MCP servers](https://opencode.ai/docs/mcp-servers/)
- [OpenAI Codex MCP setup](https://developers.openai.com/learn/docs-mcp)
- [VS Code MCP setup](https://code.visualstudio.com/docs/agent-customization/mcp-servers)
- [Cursor MCP setup](https://docs.cursor.com/context/model-context-protocol)
- [Agent Skills installer and supported agents](https://github.com/vercel-labs/skills)
