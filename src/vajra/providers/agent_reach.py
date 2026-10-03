from __future__ import annotations

import json
import shutil
import subprocess
from typing import Any


class AgentReachProvider:
    """Read-only adapter for Agent Reach's upstream capability/doctor interface."""

    name = "agent-reach"
    timeout_seconds = 20

    def executable(self) -> str | None:
        return shutil.which("agent-reach")

    def capabilities(self) -> dict[str, Any]:
        exe = self.executable()
        if not exe:
            return {"status": "unavailable", "message": "agent-reach executable not found", "channels": {}}
        try:
            result = subprocess.run([exe, "doctor", "--json"], capture_output=True, text=True,
                                    timeout=self.timeout_seconds, check=False, shell=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            return {"status": "error", "message": f"doctor failed: {type(exc).__name__}", "channels": {}}
        if result.returncode != 0:
            return {"status": "error", "message": f"doctor exited {result.returncode}", "channels": {}}
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"status": "error", "message": "doctor did not return JSON", "channels": {}}
        channels = {}
        for key, item in payload.items():
            if not isinstance(item, dict):
                continue
            channels[str(key)] = {
                "name": str(item.get("name") or key),
                "status": str(item.get("status") or "unknown"),
                "backends": list(item.get("backends") or []),
                "active_backend": item.get("active_backend"),
                "tier": item.get("tier"),
            }
        healthy = sum(item["status"] == "ok" for item in channels.values())
        return {"status": "ok" if channels else "error", "message": f"{healthy}/{len(channels)} channels currently healthy",
                "version": self.version(exe), "channels": channels}

    def version(self, exe: str | None = None) -> str | None:
        exe = exe or self.executable()
        if not exe:
            return None
        try:
            result = subprocess.run([exe, "version"], capture_output=True, text=True,
                                    timeout=5, check=False, shell=False)
        except (OSError, subprocess.TimeoutExpired):
            return None
        return result.stdout.strip() if result.returncode == 0 else None

    def check_update(self) -> dict[str, str]:
        """Ask the upstream read-only update command; never install or modify Agent Reach."""
        exe = self.executable()
        if not exe:
            return {"status": "unavailable", "message": "agent-reach executable not found"}
        try:
            result = subprocess.run([exe, "check-update"], capture_output=True, text=True,
                                    timeout=30, check=False, shell=False)
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "upstream update check timed out"}
        except OSError as exc:
            return {"status": "error", "message": f"upstream update check failed: {type(exc).__name__}"}
        # Upstream is responsible for formatting and credential scrubbing; include no stderr on failure.
        output = result.stdout.strip()[:4000]
        return {"status": "checked" if result.returncode == 0 else "error",
                "message": output if output else f"agent-reach check-update exited {result.returncode}"}
