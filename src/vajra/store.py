from __future__ import annotations

import json
import os
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any


def default_data_dir() -> Path:
    if os.environ.get("VAJRA_DATA_DIR"):
        return Path(os.environ["VAJRA_DATA_DIR"]).expanduser().resolve()
    if os.name == "nt" and os.environ.get("LOCALAPPDATA"):
        return Path(os.environ["LOCALAPPDATA"]) / "Vajra"
    return Path.home() / ".local" / "share" / "vajra"


class ResearchStore:
    def __init__(self, path: Path | None = None) -> None:
        self.data_dir = (path or default_data_dir()).expanduser().resolve()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_dir / "vajra.sqlite3"
        self._initialize()

    def connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.db_path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("PRAGMA journal_mode=WAL")
        return db

    def _initialize(self) -> None:
        with closing(self.connect()) as db, db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS runs (
                    id TEXT PRIMARY KEY, question TEXT NOT NULL, mode TEXT NOT NULL,
                    created_at TEXT NOT NULL, status TEXT NOT NULL, trace_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS sources (
                    run_id TEXT NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
                    source_id TEXT NOT NULL, url TEXT NOT NULL, content_hash TEXT NOT NULL,
                    retrieved_at TEXT NOT NULL, payload_json TEXT NOT NULL, text TEXT NOT NULL,
                    PRIMARY KEY(run_id, source_id)
                );
                CREATE TABLE IF NOT EXISTS evidence (
                    run_id TEXT NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
                    evidence_id TEXT NOT NULL, source_id TEXT NOT NULL, passage TEXT NOT NULL,
                    start_offset INTEGER NOT NULL, end_offset INTEGER NOT NULL, relevance REAL NOT NULL,
                    PRIMARY KEY(run_id, evidence_id),
                    FOREIGN KEY(run_id, source_id) REFERENCES sources(run_id, source_id)
                );
                CREATE TABLE IF NOT EXISTS claims (
                    run_id TEXT NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
                    claim_id TEXT NOT NULL, text TEXT NOT NULL, status TEXT NOT NULL,
                    evidence_ids_json TEXT NOT NULL, notes TEXT NOT NULL,
                    PRIMARY KEY(run_id, claim_id)
                );
                CREATE TABLE IF NOT EXISTS conflicts (
                    run_id TEXT NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
                    claim_a TEXT NOT NULL, claim_b TEXT NOT NULL, reason TEXT NOT NULL,
                    PRIMARY KEY(run_id, claim_a, claim_b)
                );
                CREATE INDEX IF NOT EXISTS idx_sources_url ON sources(url);
                CREATE INDEX IF NOT EXISTS idx_evidence_source ON evidence(source_id);
            """)

    def save(self, trace: dict[str, Any]) -> None:
        with closing(self.connect()) as db, db:
            db.execute("INSERT OR REPLACE INTO runs(id,question,mode,created_at,status,trace_json) VALUES(?,?,?,?,?,?)",
                       (trace["research_id"], trace["question"], trace["mode"], trace["timestamp"], trace["status"],
                        json.dumps(trace, ensure_ascii=False)))
            run_id = trace["research_id"]
            for src in trace.get("sources", []):
                payload = {k: v for k, v in src.items() if k != "text"}
                db.execute("INSERT OR REPLACE INTO sources VALUES(?,?,?,?,?,?,?)",
                           (run_id, src["source_id"], src["url"], src["content_hash"], src["retrieved_at"],
                            json.dumps(payload, ensure_ascii=False), src["text"]))
            for ev in trace.get("evidence", []):
                db.execute("INSERT OR REPLACE INTO evidence VALUES(?,?,?,?,?,?,?)",
                           (run_id, ev["evidence_id"], ev["source_id"], ev["passage"], ev["start_offset"],
                            ev["end_offset"], ev["relevance"]))
            for claim in trace.get("claims", []):
                db.execute("INSERT OR REPLACE INTO claims VALUES(?,?,?,?,?,?)",
                           (run_id, claim["claim_id"], claim["text"], claim["status"],
                            json.dumps(claim.get("evidence_ids", [])), claim.get("notes", "")))
            for conflict in trace.get("contradictions", []):
                db.execute("INSERT OR REPLACE INTO conflicts VALUES(?,?,?,?)",
                           (run_id, conflict["claim_a"], conflict["claim_b"], conflict["reason"]))

    def get(self, research_id: str) -> dict[str, Any] | None:
        if not research_id or any(ch not in "0123456789abcdef" for ch in research_id.lower()) or len(research_id) != 32:
            return None
        with closing(self.connect()) as db, db:
            row = db.execute("SELECT trace_json FROM runs WHERE id=?", (research_id,)).fetchone()
        return json.loads(row[0]) if row else None

    def count_runs(self) -> int:
        with self.connect() as db:
            return int(db.execute("SELECT count(*) FROM runs").fetchone()[0])
