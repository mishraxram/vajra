from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class SearchHit:
    url: str
    title: str = ""
    snippet: str = ""
    publisher: str = ""
    published_at: str | None = None
    provider: str = "unknown"


@dataclass(frozen=True)
class FetchedSource:
    source_id: str
    url: str
    final_url: str
    title: str
    author: str
    publisher: str
    published_at: str | None
    retrieved_at: str
    content_hash: str
    text: str
    source_type: str = "web"
    provider: str = "unknown"


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    source_id: str
    passage: str
    start_offset: int
    end_offset: int
    relevance: float


@dataclass(frozen=True)
class Claim:
    claim_id: str
    text: str
    status: str
    evidence_ids: tuple[str, ...] = field(default_factory=tuple)
    notes: str = ""


def jsonable(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        data = asdict(value)
        return {k: jsonable(v) for k, v in data.items()}
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    return value
