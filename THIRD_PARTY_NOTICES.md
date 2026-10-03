# Third-party notices

Vajra does not vendor third-party source code. Runtime dependency versions are pinned in `uv.lock`. Direct dependency licensing was checked from project metadata and upstream sources. The following resolved runtime inventory was collected with `pip-licenses` from a fresh Windows CPython 3.13 environment on 2026-10-03. Conditional packages may differ on other platforms; review the licenses for the target platform before redistributing artifacts.

| Package | Version | License | Role |
|---|---:|---|---|
| Agent Reach | 1.5.0 (external install) | MIT | Optional upstream capability/health CLI and skill; not bundled or installed by Vajra. |
| DDGS | 9.16.0 | MIT | Optional metasearch adapter. |
| MCP Python SDK (`mcp`) | 2.2.0 | MIT | Optional local stdio MCP server. |
| setuptools | 80.9.0 | MIT | Build backend. |
| PyJWT | 2.15.1 | MIT | MCP SDK transitive dependency. |
| annotated-types | 0.8.0 | MIT | Pydantic transitive dependency. |
| anyio | 4.15.1 | MIT | Async I/O transitive dependency. |
| attrs | 26.1.0 | MIT | JSON Schema transitive dependency. |
| cffi | 2.1.1 | MIT-0 | Conditional cryptography transitive dependency. |
| click | 8.5.0 | BSD-3-Clause | DDGS/MCP transitive dependency. |
| cryptography | 50.0.2 | Apache-2.0 OR BSD-3-Clause | MCP transitive dependency. |
| h11 | 0.16.0 | MIT | ASGI server transitive dependency. |
| httpcore2 | 2.13.1 | BSD-3-Clause | HTTP client transitive dependency. |
| httpx2 | 2.13.1 | BSD-3-Clause | MCP transitive dependency. |
| idna | 3.20 | BSD-3-Clause | HTTP client transitive dependency. |
| jsonschema | 4.26.0 | MIT | MCP transitive dependency. |
| jsonschema-specifications | 2025.9.1 | MIT | JSON Schema transitive dependency. |
| lxml | 6.1.3 | BSD-3-Clause | DDGS transitive dependency. |
| mcp-types | 2.2.0 | MIT | MCP SDK transitive dependency. |
| opentelemetry-api | 1.45.0 | Apache-2.0 | MCP transitive dependency. |
| primp | 2.0.1 | MIT | DDGS transitive dependency. |
| pycparser | 3.0 | BSD-3-Clause | Conditional CFFI transitive dependency. |
| pydantic | 2.13.5 | MIT | MCP transitive dependency. |
| pydantic-core | 2.46.5 | MIT | Pydantic transitive dependency. |
| python-multipart | 0.0.32 | Apache-2.0 | MCP transitive dependency. |
| pywin32 | 312 | PSF License | Windows MCP transitive dependency. |
| referencing | 0.37.0 | MIT | JSON Schema transitive dependency. |
| rpds-py | 2026.6.3 | MIT | JSON Schema transitive dependency. |
| sse-starlette | 3.5.0 | BSD-3-Clause | MCP transitive dependency. |
| starlette | 1.7.0 | BSD-3-Clause | MCP transitive dependency. |
| truststore | 0.10.4 | MIT | HTTP client transitive dependency. |
| typing-inspection | 0.4.4 | MIT | Pydantic transitive dependency. |
| typing-extensions | 4.16.0 | PSF-2.0 | Runtime typing compatibility. |
| uvicorn | 0.54.0 | BSD-3-Clause | MCP transitive dependency. |

The resolved license inventory was generated using `pip-licenses`; package metadata can omit or normalize license text. The list is an inventory, not legal advice. Preserve each dependency's actual license and notices when redistributing. `uv` is developer tooling and is not a project runtime dependency.

## Upstream references

- [Agent Reach repository and MIT license](https://github.com/Panniantong/Agent-Reach)
- [DDGS repository](https://github.com/deedy5/ddgs)
- [MCP Python SDK repository](https://github.com/modelcontextprotocol/python-sdk)
- [setuptools license](https://github.com/pypa/setuptools/blob/main/LICENSE)
- [uv license](https://github.com/astral-sh/uv/blob/main/LICENSE-APACHE)

Search engines and websites accessed by DDGS or direct fetching retain their terms and policies. Vajra does not grant permission to scrape, store, or redistribute their content.
