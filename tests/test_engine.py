import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from vajra.engine import audit_trace, run_research
from vajra.models import FetchedSource, SearchHit
from vajra.store import ResearchStore


class FakeSearch:
    name = "fake-search"

    def search(self, query, limit=5):
        return [SearchHit(url="https://example.org/report", title="Example source", provider=self.name)]


class EngineTests(unittest.TestCase):
    def test_research_persists_replayable_exact_evidence(self):
        text = "\n".join([
            "The method has a measured result in a controlled study and the sample was limited.",
            "Independent reviewers reported that the evidence remains incomplete for this population.",
        ])
        fake_source = FetchedSource(source_id="source-a", url="https://example.org/report", final_url="https://example.org/report",
            title="Example source", author="Example Author", publisher="Example", published_at="2026-01-02", retrieved_at="2026-10-03T00:00:00+00:00",
            content_hash="sha256-test", text=text, provider="direct-fetch")
        with tempfile.TemporaryDirectory() as temp:
            store = ResearchStore(Path(temp))
            with patch("vajra.engine.fetch_source", return_value=fake_source):
                trace = run_research("measured result study evidence", mode="standard", store=store, search_provider=FakeSearch())
            self.assertEqual(trace["status"], "completed")
            self.assertTrue(trace["claims"])
            self.assertTrue(all(claim["status"] == "PARTIALLY_VERIFIED" for claim in trace["claims"]))
            self.assertTrue(audit_trace(trace)["valid"])
            replay = store.get(trace["research_id"])
            self.assertEqual(replay, trace)
            self.assertTrue((Path(temp) / "reports" / f"{trace['research_id']}.research.json").exists())

    def test_failed_search_is_visible_and_does_not_fake_sources(self):
        class BrokenSearch:
            name = "broken"
            def search(self, query, limit=5):
                raise RuntimeError("backend down")
        with tempfile.TemporaryDirectory() as temp:
            trace = run_research("a question", store=ResearchStore(Path(temp)), search_provider=BrokenSearch())
            self.assertEqual(trace["status"], "failed")
            self.assertEqual(trace["sources"], [])
            self.assertTrue(trace["failures"])

    def test_audit_detects_tampered_span(self):
        trace = {"sources": [{"source_id": "s", "text": "quote here", "url": "https://example.org"}],
                 "evidence": [{"evidence_id": "e", "source_id": "s", "passage": "quote", "start_offset": 0, "end_offset": 5}],
                 "claims": [{"claim_id": "c", "evidence_ids": ["e"]}], "citations": [{"source_id": "s"}]}
        trace["evidence"][0]["passage"] = "wrong"
        self.assertFalse(audit_trace(trace)["valid"])


if __name__ == "__main__":
    unittest.main()
