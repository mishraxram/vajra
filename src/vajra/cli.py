from __future__ import annotations

import argparse
import json
import logging
import sys
from contextlib import closing
from pathlib import Path

from vajra import __version__
from vajra.engine import MODES, audit_trace, run_research
from vajra.providers.agent_reach import AgentReachProvider
from vajra.providers.search import DDGSSearchProvider
from vajra.store import ResearchStore


def _store(path: str | None) -> ResearchStore:
    return ResearchStore(Path(path) if path else None)


def _doctor(store: ResearchStore) -> int:
    agent_reach = AgentReachProvider().capabilities()
    search_status, search_message = DDGSSearchProvider().health()
    try:
        with closing(store.connect()) as db, db:
            db.execute("SELECT 1").fetchone()
        database = {"status": "ok", "path": str(store.db_path), "runs": store.count_runs()}
    except Exception as exc:
        database = {"status": "error", "error": type(exc).__name__}
    try:
        from mcp.server import MCPServer  # noqa: F401
        mcp = {"status": "configured", "transport": "stdio"}
    except ImportError:
        mcp = {"status": "missing_required_dependency", "install": "uv tool install git+https://github.com/mishraxram/vajra.git"}
    checks = {"vajra": {"status": "ok", "version": __version__}, "database": database,
              "search": {"status": search_status, "message": search_message, "network": "not probed"},
              "agent_reach": agent_reach, "mcp": mcp,
              "claim_verification": {"status": "limited", "detail": "Exact passage audit is implemented; source authority/truth not established."},
              "test_status": "not run by doctor"}
    required_ok = database["status"] == "ok" and search_status == "configured" and mcp["status"] == "configured"
    overall = "CONFIGURED" if required_ok else "DEGRADED"
    print(json.dumps({"overall": overall, "checks": checks}, ensure_ascii=False, indent=2))
    return 0 if database["status"] == "ok" else 2


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="vajra", description="Evidence before answers.")
    parser.add_argument("--data-dir", help="Local Vajra data directory (or set VAJRA_DATA_DIR)")
    parser.add_argument("--version", action="version", version=f"vajra {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor", help="Check local dependencies and provider health")
    commands.add_parser("upstream-check", help="Check Agent Reach for upstream updates without installing them")
    research = commands.add_parser("research", help="Run bounded source discovery, retrieval, and evidence capture")
    research.add_argument("question")
    research.add_argument("--mode", choices=sorted(MODES), default="standard")
    replay = commands.add_parser("replay", help="Print a saved research trace as JSON")
    replay.add_argument("research_id")
    audit = commands.add_parser("audit", help="Audit evidence spans and citation IDs in a saved run")
    audit.add_argument("research_id")
    commands.add_parser("mcp", help="Run the local stdio MCP server for compatible AI clients")
    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, stream=sys.stderr,
                        format="%(asctime)s %(levelname)s %(name)s %(message)s")
    logging.getLogger("primp").setLevel(logging.WARNING)
    args = _parser().parse_args(argv)
    store = _store(args.data_dir)
    if args.command == "doctor":
        return _doctor(store)
    if args.command == "upstream-check":
        result = AgentReachProvider().check_update()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "checked" else 1
    if args.command == "research":
        try:
            trace = run_research(args.question, args.mode, store=store)
        except Exception as exc:
            print(f"Research failed: {type(exc).__name__}: {exc}", file=sys.stderr)
            return 2
        report = store.data_dir / "reports" / f"{trace['research_id']}.md"
        print(json.dumps({"research_id": trace["research_id"], "status": trace["status"],
                          "sources": len(trace["sources"]), "evidence": len(trace["evidence"]),
                          "report": str(report), "trace": str(report.with_suffix('.research.json'))}, ensure_ascii=False, indent=2))
        return 0 if trace["status"] == "completed" else 1
    if args.command in {"replay", "audit"}:
        trace = store.get(args.research_id)
        if trace is None:
            print("Research run not found", file=sys.stderr)
            return 2
        if args.command == "replay":
            print(json.dumps(trace, ensure_ascii=False, indent=2))
            return 0
        result = audit_trace(trace)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["valid"] else 1
    if args.command == "mcp":
        try:
            from vajra.mcp_server import create_server
            create_server(store).run()
        except ImportError:
            print("MCP dependency is missing. Reinstall Vajra: uv tool install git+https://github.com/mishraxram/vajra.git", file=sys.stderr)
            return 2
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
