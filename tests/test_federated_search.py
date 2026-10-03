import unittest
from unittest.mock import patch

from vajra.models import SearchHit
from vajra.providers.federated_search import FederatedSearchProvider


class FreeSearchRoutingTests(unittest.TestCase):
    def test_default_route_is_free_ddgs_and_records_fallback_attempts(self):
        class FakeDDGS:
            last_attempts = [
                {"backend": "auto", "status": "error", "error_type": "TimeoutError"},
                {"backend": "duckduckgo", "status": "ok", "result_count": 1},
            ]

            def __init__(self, timeout):
                self.timeout = timeout

            def search(self, query, limit=5):
                self.last_attempts = type(self).last_attempts
                self.timeout_seen = self.timeout
                return [SearchHit(url="https://example.org/a", title="A", provider="ddgs:duckduckgo")]

        with patch("vajra.providers.federated_search.DDGSSearchProvider", FakeDDGS):
            provider = FederatedSearchProvider()
            hits = provider.search("question")

        self.assertEqual(provider.name, "ddgs-free-public-search")
        self.assertEqual(provider.ddgs.timeout, 5)
        self.assertEqual(len(hits), 1)
        self.assertEqual(provider.last_attempts[-1]["backend"], "duckduckgo")
        self.assertFalse(hasattr(provider, "agent_reach"))


if __name__ == "__main__":
    unittest.main()
