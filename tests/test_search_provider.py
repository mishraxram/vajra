import sys
import types
import unittest
from unittest.mock import patch

from vajra.providers.search import DDGSSearchProvider


class SearchFallbackTests(unittest.TestCase):
    def test_parser_accepts_iterable_rows(self):
        provider = DDGSSearchProvider(timeout=1)
        rows = iter([{"href": "https://example.org/source", "title": "A source", "body": "snippet"}])
        self.assertEqual(provider._hits(rows, "duckduckgo")[0].url, "https://example.org/source")

    def test_falls_back_to_direct_engine_and_records_route(self):
        calls = []

        class FakeDDGS:
            def __init__(self, timeout):
                self.timeout = timeout

            def text(self, query, max_results, backend):
                calls.append(backend)
                if backend == "auto":
                    raise RuntimeError("aggregator rate-limited")
                if backend == "duckduckgo":
                    return [{"href": "https://example.org/source", "title": "A source", "body": "snippet"}]
                return []

        with patch.dict(sys.modules, {"ddgs": types.SimpleNamespace(DDGS=FakeDDGS)}):
            provider = DDGSSearchProvider(timeout=1)
            hits = provider.search("test query", limit=3)

        self.assertEqual(calls, ["auto", "duckduckgo"])
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0].provider, "ddgs:duckduckgo")
        self.assertEqual(provider.last_attempts[-1]["status"], "ok")

    def test_raises_if_all_backends_return_empty(self):
        class EmptyDDGS:
            def __init__(self, timeout):
                pass

            def text(self, query, max_results, backend):
                return []

        with patch.dict(sys.modules, {"ddgs": types.SimpleNamespace(DDGS=EmptyDDGS)}):
            provider = DDGSSearchProvider(timeout=1)
            with self.assertRaisesRegex(RuntimeError, "all backends returned no results"):
                provider.search("test query")
        self.assertEqual(len(provider.last_attempts), 4)
        self.assertTrue(all(item["status"] == "empty" for item in provider.last_attempts))


if __name__ == "__main__":
    unittest.main()
