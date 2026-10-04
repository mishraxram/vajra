import json
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from vajra.cli import _doctor_report
from vajra.providers.agent_reach import AgentReachProvider
from vajra.providers.search import DDGSSearchProvider
from vajra.store import ResearchStore


class SearchHealthTests(unittest.TestCase):
    def test_health_is_configured_when_ddgs_imports(self):
        with patch.dict(sys.modules, {"ddgs": types.SimpleNamespace()}):
            self.assertEqual(DDGSSearchProvider().health()[0], "configured")

    def test_health_is_unavailable_when_ddgs_is_missing(self):
        with patch.dict(sys.modules, {"ddgs": None}):
            self.assertEqual(DDGSSearchProvider().health()[0], "unavailable")


class AgentReachHealthTests(unittest.TestCase):
    def setUp(self):
        self.provider = AgentReachProvider()
        self.which = patch.object(self.provider, "executable", return_value="agent-reach")
        self.which.start()
        self.addCleanup(self.which.stop)

    def test_agent_reach_absent(self):
        with patch.object(self.provider, "executable", return_value=None):
            self.assertEqual(self.provider.capabilities()["status"], "unavailable")

    @patch("vajra.providers.agent_reach.subprocess.run")
    def test_valid_json_and_version(self, run):
        run.side_effect = [
            types.SimpleNamespace(returncode=0, stdout=json.dumps({
                "web": {"name": "Web", "status": "ok", "backends": ["public"],
                        "active_backend": "public", "tier": 1},
                "invalid": "ignored",
            })),
            types.SimpleNamespace(returncode=0, stdout="Agent Reach 1.0"),
        ]
        result = self.provider.capabilities()
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["channels"]["web"]["backends"], ["public"])
        self.assertNotIn("invalid", result["channels"])
        self.assertEqual(result["version"], "Agent Reach 1.0")
        self.assertTrue(all(call.kwargs["shell"] is False for call in run.call_args_list))

    @patch("vajra.providers.agent_reach.subprocess.run")
    def test_malformed_json(self, run):
        run.return_value = types.SimpleNamespace(returncode=0, stdout="not json")
        self.assertEqual(self.provider.capabilities()["message"], "doctor did not return JSON")

    @patch("vajra.providers.agent_reach.subprocess.run", side_effect=subprocess.TimeoutExpired("agent-reach", 20))
    def test_timeout(self, _run):
        result = self.provider.capabilities()
        self.assertEqual(result["status"], "error")
        self.assertIn("TimeoutExpired", result["message"])

    @patch("vajra.providers.agent_reach.subprocess.run")
    def test_nonzero_exit(self, run):
        run.return_value = types.SimpleNamespace(returncode=7, stdout="", stderr="secret detail")
        result = self.provider.capabilities()
        self.assertEqual(result["message"], "doctor exited 7")
        self.assertNotIn("secret detail", result["message"])

    @patch("vajra.providers.agent_reach.subprocess.run", side_effect=OSError("not executable"))
    def test_os_error(self, _run):
        self.assertIn("doctor failed: OSError", self.provider.capabilities()["message"])

    @patch("vajra.providers.agent_reach.subprocess.run")
    def test_empty_valid_json_has_error_status_and_no_version_check(self, run):
        run.return_value = types.SimpleNamespace(returncode=0, stdout="{}")
        result = self.provider.capabilities()
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["channels"], {})
        self.assertEqual(run.call_count, 2)  # doctor JSON and the separate version query

    @patch("vajra.providers.agent_reach.subprocess.run", side_effect=subprocess.TimeoutExpired("agent-reach", 5))
    def test_version_timeout_returns_none(self, _run):
        self.assertIsNone(self.provider.version("agent-reach"))

    @patch("vajra.providers.agent_reach.subprocess.run")
    def test_check_update_success_and_failure(self, run):
        run.return_value = types.SimpleNamespace(returncode=0, stdout="up to date")
        self.assertEqual(self.provider.check_update(), {"status": "checked", "message": "up to date"})
        run.return_value = types.SimpleNamespace(returncode=2, stdout="")
        self.assertEqual(self.provider.check_update()["status"], "error")

    @patch("vajra.providers.agent_reach.subprocess.run", side_effect=subprocess.TimeoutExpired("agent-reach", 30))
    def test_check_update_timeout(self, _run):
        self.assertEqual(self.provider.check_update()["message"], "upstream update check timed out")

    @patch("vajra.providers.agent_reach.subprocess.run", side_effect=OSError("missing"))
    def test_check_update_os_error(self, _run):
        self.assertEqual(self.provider.check_update()["status"], "error")

    def test_doctor_report_contains_total_health_tuple(self):
        with tempfile.TemporaryDirectory() as directory:
            report = _doctor_report(ResearchStore(Path(directory)), include_agent_reach=False)
        self.assertEqual(report["checks"]["search"]["status"], "configured")
        self.assertEqual(report["overall"], "CONFIGURED")


if __name__ == "__main__":
    unittest.main()
