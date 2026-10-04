"""Build, isolate, install, and exercise the public wheel entry points."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from mcp import Client, StdioServerParameters


def _run(command: list[str], *, env: dict[str, str], cwd: Path) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {command!r}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def _python_in(venv: Path) -> Path:
    return venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def _cli_in(venv: Path) -> Path:
    return venv / ("Scripts/vajra.exe" if os.name == "nt" else "bin/vajra")


async def _smoke_mcp(cli: Path, env: dict[str, str]) -> None:
    params = StdioServerParameters(command=str(cli), args=["mcp"], env=env)
    async with Client(params) as client:
        response = await client.list_tools()
    names = {tool.name for tool in response.tools}
    expected = {"vajra_research", "vajra_replay", "vajra_audit", "agent_reach_status"}
    if names != expected:
        raise RuntimeError(f"Unexpected installed MCP tool list: {sorted(names)}")
    print("PASS installed wheel MCP server construction and tool listing")


def smoke(wheel: Path | None) -> None:
    root = Path(__file__).resolve().parents[1]
    uv = shutil.which("uv")
    if not uv:
        raise RuntimeError("uv is required to build and install the smoke-test wheel")
    with tempfile.TemporaryDirectory(prefix="vajra-wheel-smoke-") as directory:
        temporary = Path(directory)
        if wheel is None:
            wheel_dir = temporary / "wheel"
            wheel_dir.mkdir()
            _run([uv, "build", "--wheel", "--out-dir", str(wheel_dir)],
                 env=os.environ.copy(), cwd=root)
            wheels = list(wheel_dir.glob("vajra_research-*.whl"))
            if len(wheels) != 1:
                raise RuntimeError(f"Expected one freshly built wheel, found {len(wheels)}")
            wheel = wheels[0]
        elif not wheel.is_file():
            raise FileNotFoundError(f"Wheel does not exist: {wheel}")
        venv = temporary / "venv"
        _run([uv, "venv", "--python", sys.executable, str(venv)], env=os.environ.copy(), cwd=root)
        python = _python_in(venv)
        _run([uv, "pip", "install", "--python", str(python), str(wheel)],
             env=os.environ.copy(), cwd=root)

        home = temporary / "home"
        data = temporary / "data"
        home.mkdir()
        data.mkdir()
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        env.pop("PYTHONHOME", None)
        env.update({"HOME": str(home), "USERPROFILE": str(home), "VAJRA_DATA_DIR": str(data)})
        if os.name == "nt":
            env["LOCALAPPDATA"] = str(home / "AppData" / "Local")
            env["APPDATA"] = str(home / "AppData" / "Roaming")
            system_path = os.pathsep.join(filter(None, (env.get("SYSTEMROOT"),
                str(Path(env.get("SYSTEMROOT", "C:/Windows")) / "System32"))))
            env["PATH"] = os.pathsep.join((str(_cli_in(venv).parent), system_path))
        else:
            env["PATH"] = str(_cli_in(venv).parent)

        _run([str(python), "-c", "import vajra; print(vajra.__version__)"], env=env, cwd=temporary)
        print("PASS installed wheel import without PYTHONPATH")
        _run([str(_cli_in(venv)), "--help"], env=env, cwd=temporary)
        print("PASS installed `vajra --help`")
        welcome = _run([str(_cli_in(venv)), "welcome"], env=env, cwd=temporary)
        if "VAJRA" not in welcome.stdout:
            raise RuntimeError("Installed `vajra welcome` did not print the VAJRA banner")
        print("PASS installed `vajra welcome`")
        doctor = _run([str(_cli_in(venv)), "doctor"], env=env, cwd=temporary)
        doctor_report = json.loads(doctor.stdout)
        if doctor_report["checks"]["search"]["status"] != "configured":
            raise RuntimeError(f"Installed doctor search health is unexpected: {doctor_report}")
        if doctor_report["checks"]["agent_reach"]["status"] != "unavailable":
            raise RuntimeError("Isolated smoke environment unexpectedly found Agent Reach")
        print("PASS installed `vajra doctor` in an isolated home")
        _run([str(_cli_in(venv)), "research", "--help"], env=env, cwd=temporary)
        print("PASS installed `vajra research --help`")
        asyncio.run(_smoke_mcp(_cli_in(venv), env))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wheel", type=Path, nargs="?", help="Built wheel (default: build a fresh wheel first)")
    args = parser.parse_args()
    smoke(args.wheel.resolve() if args.wheel else None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
