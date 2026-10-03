"""Score saved Vajra traces against human-adjudicated exact evidence spans.

This intentionally does not score factual truth or semantic entailment. See
benchmarks/README.md before interpreting the output.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from vajra.engine import audit_trace  # noqa: E402

_CASE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,99}$")


def _normalize(text: str) -> str:
    return " ".join(text.casefold().split())


def score_case(case: dict[str, Any], trace: dict[str, Any]) -> dict[str, Any]:
    expected = case.get("expected_evidence", [])
    if not isinstance(expected, list) or any(not isinstance(item, str) or not item.strip() for item in expected):
        raise ValueError(f"case {case.get('case_id')!r}: expected_evidence must be non-empty strings")
    passages = [_normalize(str(item.get("passage", ""))) for item in trace.get("evidence", [])]
    matched = [item for item in expected if any(_normalize(item) in passage for passage in passages)]
    claims = trace.get("claims", [])
    evidence_ids = {str(item.get("evidence_id")) for item in trace.get("evidence", [])}
    structurally_supported = sum(
        bool(claim.get("evidence_ids")) and all(str(ref) in evidence_ids for ref in claim["evidence_ids"])
        for claim in claims
    )
    audit = audit_trace(trace)
    return {
        "case_id": case["case_id"],
        "research_id": trace.get("research_id"),
        "trace_integrity_valid": audit["valid"],
        "trace_integrity_issues": audit["issues"],
        "expected_evidence_count": len(expected),
        "exact_evidence_matches": len(matched),
        "evidence_coverage": len(matched) / len(expected) if expected else None,
        "unmatched_expected_evidence": [item for item in expected if item not in matched],
        "source_count": len(trace.get("sources", [])),
        "claim_count": len(claims),
        "structurally_supported_claim_ratio": structurally_supported / len(claims) if claims else None,
        "candidate_contradiction_count": len(trace.get("contradictions", [])),
        "recorded_latency_seconds": trace.get("timing_seconds"),
        "provider_cost": None,
        "truth_or_entailment_score": None,
    }


def run_benchmark(corpus_path: Path, traces_dir: Path) -> dict[str, Any]:
    corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
    if corpus.get("schema_version") != "1" or not isinstance(corpus.get("cases"), list):
        raise ValueError("corpus must have schema_version '1' and a cases array")
    results = []
    seen = set()
    for case in corpus["cases"]:
        case_id = case.get("case_id")
        if not isinstance(case_id, str) or not _CASE_ID.fullmatch(case_id) or case_id in seen:
            raise ValueError(f"invalid or duplicate case_id: {case_id!r}")
        seen.add(case_id)
        trace_path = traces_dir / f"{case_id}.research.json"
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
        results.append(score_case(case, trace))
    coverages = [row["evidence_coverage"] for row in results if row["evidence_coverage"] is not None]
    return {
        "schema_version": "1",
        "corpus_id": corpus.get("corpus_id", "unversioned"),
        "case_count": len(results),
        "mean_exact_evidence_coverage": sum(coverages) / len(coverages) if coverages else None,
        "integrity_pass_count": sum(bool(row["trace_integrity_valid"]) for row in results),
        "cases": results,
        "interpretation_limits": [
            "Exact phrase coverage is not semantic coverage or proof of truth.",
            "Structural claim support only checks evidence references in the trace.",
            "Provider cost, independent-source quality, entailment, and truth are not measured.",
            "A fair Agent Reach comparison requires a separately implemented and documented comparable workflow.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, required=True, help="Human-adjudicated benchmark corpus JSON")
    parser.add_argument("--traces", type=Path, required=True, help="Directory with CASE_ID.research.json files")
    parser.add_argument("--output", type=Path, help="Optional JSON output file; defaults to stdout")
    args = parser.parse_args()
    try:
        result = run_benchmark(args.corpus, args.traces)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Benchmark failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
