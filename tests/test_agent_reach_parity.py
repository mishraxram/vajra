import unittest

from vajra.providers.agent_reach import AgentReachProvider


class AgentReachParityTests(unittest.TestCase):
    def test_vajra_dynamic_channels_match_upstream_json_doctor(self):
        provider = AgentReachProvider()
        if not provider.executable():
            self.skipTest("Agent Reach CLI is not installed; parity is unavailable, not passed")
        observed = provider.capabilities()
        self.assertEqual(observed["status"], "ok", observed)
        self.assertTrue(observed["channels"], "upstream reported no channels")
        # The adapter must preserve every current upstream key/state/backend without a local channel list.
        import json
        import subprocess
        result = subprocess.run([provider.executable(), "doctor", "--json"], capture_output=True, text=True,
                                timeout=30, check=True, shell=False)
        upstream = json.loads(result.stdout)
        self.assertEqual(set(observed["channels"]), set(upstream))
        for name, value in upstream.items():
            with self.subTest(channel=name):
                self.assertEqual(observed["channels"][name]["status"], value["status"])
                self.assertEqual(observed["channels"][name]["backends"], value.get("backends", []))
                self.assertEqual(observed["channels"][name]["active_backend"], value.get("active_backend"))
                self.assertEqual(observed["channels"][name]["tier"], value.get("tier"))


if __name__ == "__main__":
    unittest.main()

