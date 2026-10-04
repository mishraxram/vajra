import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from vajra.mcp_server import create_server
from vajra.store import ResearchStore


class CapturingMCPServer:
    def __init__(self, _name, instructions=""):
        self.instructions = instructions
        self.tools = {}

    def tool(self):
        def register(function):
            self.tools[function.__name__] = function
            return function

        return register


class MCPHandlerTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.store = ResearchStore(Path(self.directory.name))
        self.patch_server = patch("mcp.server.MCPServer", CapturingMCPServer)
        self.patch_server.start()
        self.addCleanup(self.patch_server.stop)
        self.server = create_server(self.store)

    def test_research_validates_sources_and_serializes_results(self):
        trace = {"research_id": "run", "status": "completed", "sources": [1], "evidence": [1, 2],
                 "final_synthesis": "finding", "citations": ["S1"],
                 "audit": {"citation_audit": {"valid": True}}, "failures": []}
        with patch("vajra.mcp_server.run_research", return_value=trace) as research:
            result = json.loads(self.server.tools["vajra_research"]("question"))
            research.assert_called_once_with("question", "standard", store=self.store, external_sources=[])
        self.assertEqual(result["research_id"], "run")
        self.assertEqual(result["evidence"], 2)

    def test_research_rejects_invalid_or_oversized_source_payload(self):
        handler = self.server.tools["vajra_research"]
        malformed = json.loads(handler("question", sources_json="{"))
        not_array = json.loads(handler("question", sources_json="{}"))
        oversized = json.loads(handler("question", sources_json='"' + ("x" * 5_500_001) + '"'))
        self.assertIn("invalid sources_json", malformed["error"])
        self.assertIn("invalid sources_json", not_array["error"])
        self.assertIn("invalid sources_json", oversized["error"])

    def test_replay_returns_compact_trace_and_exact_text_chunk(self):
        source_text = "This is a source passage for replay verification. " * 40
        trace = {"research_id": "a" * 32, "sources": [
            {"source_id": "source", "title": "Source title", "url": "https://example.org/",
             "content_hash": "hash", "retrieved_at": "now", "text": source_text},
        ]}
        self.store.save({"research_id": "a" * 32, "question": "q", "mode": "fast",
                         "timestamp": "now", "status": "completed", **trace})
        handler = self.server.tools["vajra_replay"]
        compact = json.loads(handler("a" * 32))
        self.assertNotIn("text", compact["sources"][0])
        chunk = json.loads(handler("a" * 32, "source", 0))
        self.assertEqual(chunk["text"], source_text[chunk["offset_start"]:chunk["offset_end"]])
        self.assertIn("untrusted", chunk["trust_boundary"])
        self.assertEqual(json.loads(handler("missing")), {"error": "research run not found"})
        self.assertEqual(json.loads(handler("a" * 32, "missing"))["error"], "source not found")
        self.assertEqual(json.loads(handler("a" * 32, "source", 999))["error"], "chunk_index out of range")

    def test_audit_and_agent_reach_status_tools(self):
        trace = {"research_id": "b" * 32, "sources": []}
        self.store.save({"research_id": "b" * 32, "question": "q", "mode": "fast",
                         "timestamp": "now", "status": "completed", **trace})
        with patch("vajra.mcp_server.audit_trace", return_value={"valid": True}) as audit:
            self.assertEqual(json.loads(self.server.tools["vajra_audit"]("b" * 32)), {"valid": True})
            audit.assert_called_once_with(self.store.get("b" * 32))
        self.assertEqual(json.loads(self.server.tools["vajra_audit"]("missing")),
                         {"error": "research run not found"})
        with patch("vajra.mcp_server.AgentReachProvider.capabilities", return_value={"status": "unavailable"}):
            self.assertEqual(json.loads(self.server.tools["agent_reach_status"]()), {"status": "unavailable"})


if __name__ == "__main__":
    unittest.main()
