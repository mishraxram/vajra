import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from vajra import cli
from vajra.store import ResearchStore


class CLITests(unittest.TestCase):
    def test_help_and_research_help_exit_successfully(self):
        for args in (["--help"], ["research", "--help"]):
            with self.subTest(args=args), contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as raised:
                cli.main(list(args))
            self.assertEqual(raised.exception.code, 0)

    @patch("vajra.cli.AgentReachProvider.capabilities", return_value={"status": "unavailable"})
    def test_doctor_prints_json_and_succeeds(self, _capabilities):
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(io.StringIO()) as output:
            result = cli.main(["--data-dir", directory, "doctor"])
        self.assertEqual(result, 0)
        self.assertEqual(json.loads(output.getvalue())["checks"]["search"]["status"], "configured")

    def test_noninteractive_welcome_prints_banner_without_prompt(self):
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(io.StringIO()) as output:
            with patch("vajra.cli.sys.stdin", io.StringIO("")):
                result = cli.main(["--data-dir", directory, "welcome"])
        self.assertEqual(result, 0)
        self.assertIn("THE OPEN AGENT RESEARCH ECOSYSTEM", output.getvalue())

    def test_sources_file_rejects_invalid_json(self):
        with tempfile.TemporaryDirectory() as directory:
            source_file = Path(directory) / "sources.json"
            source_file.write_text("{", encoding="utf-8")
            with contextlib.redirect_stderr(io.StringIO()):
                result = cli.main(["--data-dir", directory, "research", "question", "--sources-file", str(source_file)])
        self.assertEqual(result, 2)

    @patch("vajra.cli.AgentReachProvider.check_update", return_value={"status": "checked"})
    def test_upstream_check_prints_status(self, _check_update):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            result = cli.main(["upstream-check"])
        self.assertEqual(result, 0)
        self.assertEqual(json.loads(output.getvalue())["status"], "checked")

    def test_replay_and_audit_existing_trace(self):
        with tempfile.TemporaryDirectory() as directory:
            store = ResearchStore(Path(directory))
            trace = {
                "research_id": "a" * 32,
                "question": "example question",
                "mode": "fast",
                "timestamp": "2026-10-04T00:00:00+00:00",
                "status": "completed",
                "sources": [], "evidence": [], "claims": [], "contradictions": [],
                "citations": [], "audit": {"citation_audit": {"valid": True}},
            }
            store.save(trace)
            with contextlib.redirect_stdout(io.StringIO()) as replay_output:
                self.assertEqual(cli.main(["--data-dir", directory, "replay", "a" * 32]), 0)
            self.assertEqual(json.loads(replay_output.getvalue())["research_id"], "a" * 32)
            with contextlib.redirect_stdout(io.StringIO()) as audit_output:
                self.assertEqual(cli.main(["--data-dir", directory, "audit", "a" * 32]), 0)
            self.assertTrue(json.loads(audit_output.getvalue())["valid"])

    @patch("vajra.cli.run_research", side_effect=RuntimeError("simulated failure"))
    def test_research_failure_is_reported_without_trace(self, _run_research):
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stderr(io.StringIO()):
            result = cli.main(["--data-dir", directory, "research", "question"])
        self.assertEqual(result, 2)

    def test_mcp_command_creates_and_runs_server(self):
        server = Mock()
        with patch("vajra.mcp_server.create_server", return_value=server), tempfile.TemporaryDirectory() as directory:
            self.assertEqual(cli.main(["--data-dir", directory, "mcp"]), 0)
        server.run.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
