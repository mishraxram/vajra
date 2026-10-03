from __future__ import annotations

import argparse
import json
import logging
import os
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


def _doctor_report(store: ResearchStore, *, include_agent_reach: bool = True) -> dict:
    agent_reach = (AgentReachProvider().capabilities() if include_agent_reach else
                   {"status": "not_checked", "message": "Run `vajra doctor` to inspect Agent Reach."})
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
        mcp = {"status": "missing_required_dependency", "install": "uv tool install --from git+https://github.com/mishraxram/vajra.git vajra-research"}
    checks = {"vajra": {"status": "ok", "version": __version__}, "database": database,
              "search": {"status": search_status, "message": search_message, "network": "not probed"},
              "agent_reach": agent_reach, "mcp": mcp,
              "claim_verification": {"status": "limited", "detail": "Exact passage audit is implemented; source authority/truth not established."},
              "test_status": "not run by doctor"}
    required_ok = database["status"] == "ok" and search_status == "configured" and mcp["status"] == "configured"
    overall = "CONFIGURED" if required_ok else "DEGRADED"
    return {"overall": overall, "checks": checks}


def _doctor(store: ResearchStore) -> int:
    result = _doctor_report(store)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["checks"]["database"]["status"] == "ok" else 2


_LOGO_GLYPHS = {
    "V": ("██    ██", "██    ██", "██    ██", " ██  ██ ", " ██  ██ ", "  ████  "),
    "A": ("  ████  ", " ██  ██ ", " ██  ██ ", " ██████ ", " ██  ██ ", " ██  ██ "),
    "J": ("   █████", "      ██", "      ██", "      ██", "██    ██", " ██████ "),
    "R": ("██████  ", "██    ██", "██    ██", "██████  ", "██  ██  ", "██    ██"),
}
_BANNER = tuple("  ".join(_LOGO_GLYPHS[letter][row] for letter in "VAJRA") for row in range(6))


def _show_banner() -> None:
    color = sys.stdout.isatty() and (
        os.name != "nt" or any(os.environ.get(name) for name in ("WT_SESSION", "TERM", "ANSICON"))
    )
    white, gray, reset = ("\033[1;37m", "\033[38;5;244m", "\033[0m") if color else ("", "", "")
    print(white + "\n".join(_BANNER) + reset)
    print(f"\n      {white}THE OPEN AGENT RESEARCH ECOSYSTEM{reset}")
    print(f"{gray}─────────────────────────────────────────────────────────────────{reset}\n")


def _run_research(question: str, mode: str, store: ResearchStore, *, as_json: bool = False,
                  show_banner: bool = True) -> int:
    if show_banner and sys.stdout.isatty():
        _show_banner()
    try:
        trace = run_research(question, mode, store=store)
    except Exception as exc:
        print(f"Research failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    report = store.data_dir / "reports" / f"{trace['research_id']}.md"
    trace_path = report.with_suffix(".research.json")
    result = {"research_id": trace["research_id"], "status": trace["status"],
              "sources": len(trace["sources"]), "evidence": len(trace["evidence"]),
              "findings": trace["final_synthesis"], "citations": trace["citations"],
              "citation_audit": trace["audit"]["citation_audit"],
              "report": str(report), "trace": str(trace_path)}
    if sys.stdout.isatty() and not as_json:
        print(f"Run {trace['research_id']} · {trace['status'].upper()} · "
              f"{result['sources']} source(s) · {result['evidence']} evidence passage(s)\n")
        print(report.read_text(encoding="utf-8").rstrip())
        print(f"\nSaved report: {report}\nSaved trace:  {trace_path}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if trace["status"] == "completed" else 1


def _welcome(store: ResearchStore) -> int:
    _show_banner()
    # First-run should be fast and only check components required for Vajra itself.
    # Agent Reach capability discovery may invoke slow upstream commands; `doctor` remains the full audit.
    health = _doctor_report(store, include_agent_reach=False)
    checks = health["checks"]
    database_ok = checks["database"]["status"] == "ok"
    if health["overall"] == "CONFIGURED":
        print(f"[✓] VAJRA installed successfully (v{__version__}). Core research components are configured.\n")
    else:
        print(f"[!] VAJRA v{__version__} is installed, but setup needs attention.")
        for name in ("database", "search", "mcp"):
            check = checks[name]
            if check["status"] not in {"ok", "configured"}:
                print(f"    {name}: {check['status']} — {check.get('message', check.get('install', check.get('error', 'check configuration')))}")
        print()
    if not sys.stdin.isatty():
        print("Run `vajra doctor` for diagnostics or `vajra research \"your question\"` to start.")
        return 0 if database_ok else 2
    try:
        question = input("vajra ➔ ").strip()
    except EOFError:
        print()
        question = ""
    if not question:
        print("Ready when you are. Run `vajra` again to start a research question.")
        return 0 if database_ok else 2
    mode = os.environ.get("VAJRA_MODE", "standard").lower()
    if mode not in MODES:
        print(f"Invalid VAJRA_MODE={mode!r}; using standard mode.", file=sys.stderr)
        mode = "standard"
    return _run_research(question, mode, store, show_banner=False)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="vajra", description="Evidence before answers.")
    parser.add_argument("--data-dir", help="Local Vajra data directory (or set VAJRA_DATA_DIR)")
    parser.add_argument("--version", action="version", version=f"vajra {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("welcome", help="Show the branded first-run check and start interactive research")
    commands.add_parser("doctor", help="Check local dependencies and provider health")
    commands.add_parser("upstream-check", help="Check Agent Reach for upstream updates without installing them")
    research = commands.add_parser("research", help="Run bounded source discovery, retrieval, and evidence capture")
    research.add_argument("question")
    research.add_argument("--mode", choices=sorted(MODES), default="standard")
    research.add_argument("--json", action="store_true", help="Always print machine-readable JSON")
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
    raw_args = list(sys.argv[1:] if argv is None else argv)
    if not raw_args and sys.stdin.isatty():
        raw_args = ["welcome"]
    args = _parser().parse_args(raw_args)
    store = _store(args.data_dir)
    if args.command == "welcome":
        return _welcome(store)
    if args.command == "doctor":
        return _doctor(store)
    if args.command == "upstream-check":
        result = AgentReachProvider().check_update()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "checked" else 1
    if args.command == "research":
        return _run_research(args.question, args.mode, store, as_json=args.json)
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
            print("MCP dependency is missing. Reinstall Vajra: uv tool install --from git+https://github.com/mishraxram/vajra.git vajra-research", file=sys.stderr)
            return 2
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
