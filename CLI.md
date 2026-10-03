# CLI

| Command | Behavior |
|---|---|
| `vajra doctor` | Reports local DB health, optional search import state, MCP SDK state, and dynamic Agent Reach doctor data; does not claim network search was verified |
| `vajra upstream-check` | Runs Agent Reach's read-only upstream update check; never installs or overwrites it |
| `vajra research QUESTION --mode fast\|standard\|deep\|forensic` | Runs bounded queries, retrieves sources, records passages and outputs Markdown/JSON; return 1 when no source was fetched, 2 for setup/runtime errors |
| `vajra replay RUN_ID` | Prints stored JSON trace |
| `vajra audit RUN_ID` | Checks exact evidence spans, claim links, and citation/source manifest |
| `vajra mcp` | Starts the optional stdio server; stdout is reserved for MCP |

Set `VAJRA_DATA_DIR` or pass global `--data-dir` to change storage. Default is `%LOCALAPPDATA%\Vajra` on Windows and `~/.local/share/vajra` elsewhere. Run `uv run --all-extras --frozen vajra --help` for current parser output.
