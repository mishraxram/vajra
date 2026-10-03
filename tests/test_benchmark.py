import json
import tempfile
import unittest
from pathlib import Path

from benchmarks.score import run_benchmark, score_case


def _trace():
    source = {"source_id": "s1", "url": "https://example.org/", "text": "A fact.",
              "title": "Example", "author": None, "publisher": "Example", "published_at": None,
              "retrieved_at": "2026-10-03T00:00:00+00:00", "content_hash": "hash"}
    evidence = {"evidence_id": "e1", "source_id": "s1", "passage": "A fact.",
                "start_offset": 0, "end_offset": 7}
    claim = {"claim_id": "c1", "text": "A fact.", "evidence_ids": ["e1"]}
    return {"research_id": "r1", "sources": [source], "evidence": [evidence], "claims": [claim],
            "citations": [{"source_id": "s1"}], "contradictions": [], "timing_seconds": 0.01}


class BenchmarkTests(unittest.TestCase):
    def test_score_case_measures_exact_span_and_trace_integrity(self):
        result = score_case({"case_id": "q1", "expected_evidence": ["fact.", "missing span"]}, _trace())
        self.assertTrue(result["trace_integrity_valid"])
        self.assertEqual(result["evidence_coverage"], 0.5)
        self.assertEqual(result["structurally_supported_claim_ratio"], 1.0)
        self.assertIsNone(result["truth_or_entailment_score"])

    def test_run_benchmark_loads_case_trace(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            corpus = root / "corpus.json"
            traces = root / "traces"
            traces.mkdir()
            corpus.write_text(json.dumps({"schema_version": "1", "corpus_id": "test-v1", "cases": [
                {"case_id": "q1", "expected_evidence": ["A fact."]}]}), encoding="utf-8")
            (traces / "q1.research.json").write_text(json.dumps(_trace()), encoding="utf-8")
            result = run_benchmark(corpus, traces)
        self.assertEqual(result["mean_exact_evidence_coverage"], 1.0)
        self.assertEqual(result["integrity_pass_count"], 1)
        self.assertIsNone(result["cases"][0]["provider_cost"])

    def test_case_id_path_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            corpus = root / "corpus.json"
            traces = root / "traces"
            traces.mkdir()
            corpus.write_text(json.dumps({"schema_version": "1", "cases": [
                {"case_id": "../escape", "expected_evidence": []}]}), encoding="utf-8")
            with self.assertRaises(ValueError):
                run_benchmark(corpus, traces)


if __name__ == "__main__":
    unittest.main()
