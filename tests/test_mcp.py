import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

try:
    from mcp import Client, StdioServerParameters
except ImportError:
    Client = None
    StdioServerParameters = None


@unittest.skipIf(Client is None, "optional MCP SDK is not installed")
class MCPTests(unittest.IsolatedAsyncioTestCase):
    async def test_status_tool_is_callable_and_dynamic(self):
        with tempfile.TemporaryDirectory() as temp:
            params = StdioServerParameters(command=sys.executable,
                args=["-m", "vajra.cli", "mcp"], env={"VAJRA_DATA_DIR": temp})
            async with Client(params) as client:
                tools = await client.list_tools()
                names = {tool.name for tool in tools.tools}
                self.assertEqual(names, {"vajra_research", "vajra_replay", "vajra_audit", "agent_reach_status"})
                research_tool = next(tool for tool in tools.tools if tool.name == "vajra_research")
                self.assertIn("sources_json", research_tool.input_schema["properties"])
                result = await client.call_tool("agent_reach_status", {})
                self.assertTrue(result.content)
                payload = json.loads(result.content[0].text)
                self.assertIn(payload["status"], {"ok", "unavailable", "error"})
                missing = await client.call_tool("vajra_audit", {"research_id": "0" * 32})
                self.assertEqual(json.loads(missing.content[0].text), {"error": "research run not found"})


if __name__ == "__main__":
    unittest.main()
