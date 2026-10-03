from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import tempfile
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

from vajra.fetch import fetch_source, select_passages
from vajra.models import Claim, Evidence, FetchedSource, jsonable
from vajra.providers.agent_reach import AgentReachProvider
from vajra.providers.search import DDGSSearchProvider, SearchProvider
from vajra.store import ResearchStore

logger = logging.getLogger("vajra")
MODES = {"fast": 1, "standard": 3, "deep": 5, "forensic": 7}
MAX_FETCHES = {"fast": 3, "standard": 6, "deep": 10, "forensic": 14}
MIN_SOURCES = {"fast": 1, "standard": 2, "deep": 3, "forensic": 3}
_NEGATIONS = {"not", "no", "never", "none", "without", "cannot", "can't", "fails", "failed", "false", "doesn't", "isn't"}


def plan_research(question: str, mode: str) -> dict[str, Any]:
    if mode not in MODES:
        raise ValueError(f"Unsupported mode: {mode}")
    question = " ".join(question.split())
    queries = [question]
    if mode in {"standard", "deep", "forensic"}:
        queries.extend([f"{question} primary source", f"{question} limitations evidence"])
    adversarial_queries: list[str] = []
    if mode in {"deep", "forensic"}:
        adversarial_queries.extend([f"{question} counterevidence", f"{question} contradictory findings"])
    if mode == "forensic":
        adversarial_queries.extend([f"{question} methodological flaws limitations", f"{question} recent contradictory update official"])
    all_queries = queries + adversarial_queries
    return {"intent": "evidence-backed research", "scope": "web sources discovered by configured search provider",
            "time_range": "unspecified; retrieval timestamps are recorded", "constraints": ["no model-generated facts", "source text is untrusted"],
            "subquestions": all_queries, "queries": queries, "adversarial_queries": adversarial_queries, "hypotheses": [],
            "source_strategy": ["search for direct evidence", "retrieve candidate source pages", "retain exact spans"],
            "adversarial_strategy": ["run a separately labeled counterevidence query pass"] if adversarial_queries else [],
            "verification_requirements": ["source fetch succeeded", "quoted passage is present at recorded offsets", "publisher/date metadata retained when available"],
            "stop_conditions": ["query budget exhausted", "source fetch cap reached", "provider failure"]}


def _claim_id(text: str) -> str:
    return hashlib.sha256(" ".join(text.split()).casefold().encode("utf-8")).hexdigest()[:24]


def _source_id(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:24]


def _completion_status(mode: str, source_count: int, failures: list[dict[str, str]]) -> str:
    if source_count == 0:
        return "failed" if failures else "insufficient_evidence"
    if failures or source_count < MIN_SOURCES[mode]:
        return "partial"
    return "completed"


def _candidate_contradictions(claims: list[dict[str, Any]]) -> list[dict[str, str]]:
    conflicts = []
    for index, left in enumerate(claims):
        left_words = {w.casefold() for w in re.findall(r"[\w-]{4,}", left["text"])}
        left_neg = bool(left_words & _NEGATIONS)
        for right in claims[index + 1:]:
            right_words = {w.casefold() for w in re.findall(r"[\w-]{4,}", right["text"])}
            union = left_words | right_words
            overlap = len(left_words & right_words) / max(len(union), 1)
            if overlap >= 0.55 and left_neg != bool(right_words & _NEGATIONS):
                conflicts.append({"claim_a": left["claim_id"], "claim_b": right["claim_id"],
                                  "reason": "Heuristic lexical/polarity mismatch; candidate only, requires human review."})
    return conflicts


def run_research(question: str, mode: str = "standard", *, store: ResearchStore | None = None,
                 search_provider: SearchProvider | None = None) -> dict[str, Any]:
    question = " ".join(question.split())
    if not question or len(question) > 2000:
        raise ValueError("Question must contain 1 to 2000 characters")
    if mode not in MODES:
        raise ValueError(f"Mode must be one of: {', '.join(MODES)}")
    store = store or ResearchStore()
    provider = search_provider or DDGSSearchProvider()
    started = time.perf_counter()
    stamp = datetime.now(timezone.utc).isoformat()
    research_id = uuid.uuid4().hex
    plan = plan_research(question, mode)
    queries = plan["queries"]
    search_results: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    fallbacks: list[dict[str, Any]] = []
    for path_name, path_queries in (("primary", plan["queries"]), ("adversarial", plan["adversarial_queries"])):
        for query in path_queries:
            try:
                hits = provider.search(query, limit=MODES[mode])
                attempts = list(getattr(provider, "last_attempts", []))
                for attempt in attempts:
                    if attempt.get("backend") != "auto":
                        fallbacks.append({"path": path_name, "query": query, "provider": provider.name, **attempt})
                search_results.append({"path": path_name, "query": query, "provider": provider.name,
                                       "attempts": attempts, "hits": [jsonable(hit) for hit in hits]})
            except Exception as exc:
                logger.warning("%s search failed (%s)", path_name, type(exc).__name__)
                attempts = list(getattr(provider, "last_attempts", []))
                for attempt in attempts:
                    if attempt.get("backend") != "auto":
                        fallbacks.append({"path": path_name, "query": query, "provider": provider.name, **attempt})
                failures.append({"stage": "search", "path": path_name, "query": query, "provider": provider.name,
                                 "attempts": json.dumps(attempts, ensure_ascii=False),
                                 "error": f"{type(exc).__name__}: {exc}"})
    unique_hits = {}
    for search in search_results:
        for hit in search["hits"]:
            url = str(hit["url"])
            unique_hits.setdefault(_source_id(url), hit)
    candidates = list(unique_hits.values())[:MAX_FETCHES[mode]]
    sources: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    claims: list[dict[str, Any]] = []

    def do_fetch(hit: dict[str, Any]) -> tuple[dict[str, Any], FetchedSource | None, str | None]:
        try:
            fetched = fetch_source(hit["url"], provider=str(hit.get("provider", "unknown")))
            return hit, fetched, None
        except Exception as exc:
            return hit, None, f"{type(exc).__name__}: {exc}"

    with ThreadPoolExecutor(max_workers=4, thread_name_prefix="vajra-fetch") as pool:
        futures = [pool.submit(do_fetch, hit) for hit in candidates]
        for future in as_completed(futures):
            hit, source, error = future.result()
            if source is None:
                failures.append({"stage": "fetch", "url": str(hit["url"]), "error": error or "unknown fetch failure"})
                continue
            source_dict = jsonable(source)
            source_dict.update({"search_title": hit.get("title", ""), "search_snippet": hit.get("snippet", ""),
                                "source_quality": "unassessed", "independence_group": source.content_hash})
            sources.append(source_dict)
            for passage, start, end, relevance in select_passages(source.text, question, limit=3):
                evidence_id = hashlib.sha256(f"{source.source_id}:{start}:{end}".encode()).hexdigest()[:24]
                ev = Evidence(evidence_id=evidence_id, source_id=source.source_id, passage=passage,
                              start_offset=start, end_offset=end, relevance=round(relevance, 4))
                evidence.append(jsonable(ev))
                claim = Claim(claim_id=_claim_id(passage), text=passage, status="PARTIALLY_VERIFIED",
                              evidence_ids=(evidence_id,),
                              notes="Exact passage is present in the fetched source; factual truth and independence are not established.")
                if not any(c["claim_id"] == claim.claim_id for c in claims):
                    claims.append(jsonable(claim))
    sources.sort(key=lambda item: item["source_id"])
    evidence.sort(key=lambda item: (-item["relevance"], item["evidence_id"]))
    claims.sort(key=lambda item: item["claim_id"])
    contradictions = _candidate_contradictions(claims) if mode in {"deep", "forensic"} else []
    status = _completion_status(mode, len(sources), failures)
    trace: dict[str, Any] = {"schema_version": "1.0", "research_id": research_id, "question": question, "timestamp": stamp,
        "mode": mode, "status": status, "plan": plan,
        "providers": [{"name": provider.name, "role": "search", "state": "used" if search_results else "failed"},
                      {"name": "direct-fetch", "role": "retrieve/extract", "state": "used" if sources else "failed"},
                      {"name": "agent-reach", "role": "capability-health", "state": "not used for content retrieval"}],
        "queries": search_results, "sources": sources, "evidence": evidence, "claims": claims,
        "contradictions": contradictions, "verification": [{"claim_id": c["claim_id"], "status": c["status"],
            "checks": ["source fetched", "passage extracted from source text"], "limitations": ["source authority and factual truth not verified"]} for c in claims],
        "citations": [{"source_id": src["source_id"], "url": src["url"], "title": src["title"], "author": src["author"], "publisher": src["publisher"],
                       "published_at": src["published_at"], "retrieved_at": src["retrieved_at"], "content_hash": src["content_hash"]} for src in sources],
        "fallbacks": fallbacks, "failures": failures, "final_synthesis": _synthesize(question, claims, sources, evidence, failures),
        "audit": {"citation_audit": "passed" if _audit_records(sources, evidence, claims)["valid"] else "failed",
                  "source_count": len(sources), "evidence_count": len(evidence), "claim_count": len(claims),
                  "unsupported_claims": 0, "notes": ["Candidate claims are source excerpts, not model-generated factual assertions.",
                     "No independent truth oracle or semantic entailment model ran."]},
        "timing_seconds": round(time.perf_counter() - started, 3)}
    store.save(trace)
    _export(trace, store.data_dir)
    return trace


def _synthesize(question: str, claims: list[dict[str, Any]], sources: list[dict[str, Any]], evidence: list[dict[str, Any]], failures: list[dict[str, str]]) -> str:
    if not claims:
        note = "No source-backed passages were collected."
        if failures:
            note += " Provider failures are recorded in the run trace."
        return note
    source_map = {item["source_id"]: item for item in sources}
    evidence_map = {item["evidence_id"]: item for item in evidence}
    ranked_claims = sorted(
        claims,
        key=lambda claim: max(
            (evidence_map.get(evidence_id, {}).get("relevance", 0) for evidence_id in claim["evidence_ids"]),
            default=0,
        ),
        reverse=True,
    )
    ranked_items = []
    for claim in ranked_claims:
        ev = evidence_map.get(claim["evidence_ids"][0])
        source = source_map.get(ev["source_id"]) if ev else None
        if ev and source:
            ranked_items.append((claim, ev, source))
    # Put the strongest passage from each distinct source first, then show
    # additional passages. This avoids letting one page dominate the answer.
    diverse_items = []
    remaining_items = []
    seen_sources = set()
    for item in ranked_items:
        if item[2]["source_id"] not in seen_sources:
            diverse_items.append(item)
            seen_sources.add(item[2]["source_id"])
        else:
            remaining_items.append(item)
    ranked_items = diverse_items + remaining_items
    lines = [
        f"## Evidence-based answer to: {_escape_markdown(question)}",
        "",
        "The passages below are ranked by relevance and quoted from fetched sources. They show what those sources say; VAJRA has not independently confirmed their factual accuracy or authority.",
        "",
        "### Most relevant findings",
    ]
    shown = 0
    for claim, _ev, source in ranked_items:
        safe_url = quote(source["url"], safe=":/?&=#%+,-._~@")
        title = _escape_markdown(source.get("title") or source["url"])
        lines.append(f"- “{_escape_markdown(claim['text'])}” — [{title}]({safe_url})")
        shown += 1
        if shown == 8:
            break
    if len(ranked_items) > shown:
        lines.append(f"- {len(ranked_items) - shown} additional passage(s) are available in the saved report trace.")
    lines.extend(["", f"Collected {len(sources)} fetched source(s) and {len(evidence)} passage(s).",
                  "Source authority, factual correctness, and independence are not verified by this run."])
    if failures:
        lines.append(f"{len(failures)} provider or fetch failure(s) occurred; see the trace.")
    return "\n".join(lines)


def _audit_records(sources: list[dict[str, Any]], evidence: list[dict[str, Any]], claims: list[dict[str, Any]]) -> dict[str, Any]:
    src_map = {item["source_id"]: item for item in sources}
    ev_map = {item["evidence_id"]: item for item in evidence}
    issues = []
    for ev in evidence:
        src = src_map.get(ev["source_id"])
        if not src or src["text"][ev["start_offset"]:ev["end_offset"]] != ev["passage"]:
            issues.append(f"Evidence span mismatch: {ev['evidence_id']}")
    for claim in claims:
        for ev_id in claim["evidence_ids"]:
            if ev_id not in ev_map:
                issues.append(f"Claim missing evidence: {claim['claim_id']}")
    return {"valid": not issues, "issues": issues}


def audit_trace(trace: dict[str, Any]) -> dict[str, Any]:
    result = _audit_records(trace.get("sources", []), trace.get("evidence", []), trace.get("claims", []))
    known_sources = {src["source_id"] for src in trace.get("sources", [])}
    cited_sources = {citation.get("source_id") for citation in trace.get("citations", [])}
    result["valid"] = result["valid"] and known_sources == cited_sources
    if known_sources != cited_sources:
        result["issues"].append("Citation manifest does not match the stored sources")
    result["source_count"] = len(known_sources)
    result["evidence_count"] = len(trace.get("evidence", []))
    result["claim_count"] = len(trace.get("claims", []))
    return result


def _escape_markdown(value: str) -> str:
    return re.sub(r"([\\`*_{}\[\]<>()#+.!|])", r"\\\1", value.replace("\r", " ").replace("\n", " "))


def _atomic_write(path: Path, content: str) -> None:
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except BaseException:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise


def _export(trace: dict[str, Any], output_dir: Path) -> None:
    reports = output_dir / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    # IDs are generated internally, but still validate before forming output paths.
    rid = str(trace["research_id"])
    if len(rid) != 32 or any(ch not in "0123456789abcdef" for ch in rid):
        raise ValueError("Invalid internal research identifier")
    json_path = reports / f"{rid}.research.json"
    md_path = reports / f"{rid}.md"
    _atomic_write(json_path, json.dumps(trace, ensure_ascii=False, indent=2))
    citation_index = {src["source_id"]: src for src in trace.get("sources", [])}
    lines = [f"# Research: {_escape_markdown(trace['question'])}", "", f"- Run: `{rid}`", f"- Time: {trace['timestamp']}",
             f"- Mode: {trace['mode']}", f"- Status: {trace['status']}", "", trace["final_synthesis"], "", "## Sources"]
    if trace["status"] in {"partial", "failed", "insufficient_evidence"}:
        lines[6:7] = ["", "> **Incomplete run:** Treat this report as preliminary. Review the recorded failures and search attempts in the JSON trace before relying on it.", ""]
    for src in citation_index.values():
        title = (src["title"] or src["url"]).replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]").replace("(", "\\(").replace(")", "\\)")
        safe_url = quote(src["url"], safe=":/?&=#%+,-._~@")
        attribution = ", ".join(part for part in [src.get("author"), src.get("publisher")] if part)
        if src.get("published_at"):
            attribution += ("; " if attribution else "") + f"published {src['published_at']}"
        details = f" — {attribution}" if attribution else ""
        lines.append(f"- [{title}]({safe_url}){details}; retrieved {src['retrieved_at']}; SHA-256 `{src['content_hash']}`")
    if not citation_index:
        lines.append("No sources were successfully fetched.")
    lines.extend(["", "## Audit", f"Citation audit: {trace['audit']['citation_audit']}.",
                  "Source text, authority, and factual truth are separate checks. See the JSON trace for queries, excerpts, and failures."])
    _atomic_write(md_path, "\n".join(lines) + "\n")
