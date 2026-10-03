import unittest

from vajra.providers.federated_search import AgentReachExaSearchProvider


class AgentReachExaParserTests(unittest.TestCase):
    def test_parses_exa_result_metadata_and_highlights(self):
        text = ("Title: Coroutines and tasks\nURL: https://docs.python.org/3/library/asyncio-task.html\n"
                "Published: N/A\nAuthor: N/A\nHighlights:\n- TaskGroup waits for related tasks.\n\n"
                "Title: Asyncio overview\nURL: https://docs.python.org/3/library/asyncio.html\n"
                "Highlights:\nGeneral asynchronous I/O.")
        parsed = AgentReachExaSearchProvider._parse_results(text)
        self.assertEqual(parsed, [
            ("Coroutines and tasks", "https://docs.python.org/3/library/asyncio-task.html",
             "- TaskGroup waits for related tasks."),
            ("Asyncio overview", "https://docs.python.org/3/library/asyncio.html",
             "General asynchronous I/O."),
        ])

    def test_skips_malformed_result_without_public_url(self):
        self.assertEqual(AgentReachExaSearchProvider._parse_results(
            "Title: Invalid\nURL: file:///private.txt\nHighlights:\nsecret"), [])


if __name__ == "__main__":
    unittest.main()
