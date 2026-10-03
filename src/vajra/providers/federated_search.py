from __future__ import annotations

from vajra.models import SearchHit
from vajra.providers.search import DDGSSearchProvider


class FederatedSearchProvider:
    """Free, keyless search using DDGS' public engine fallback chain."""

    name = "ddgs-free-public-search"

    def __init__(self) -> None:
        self.ddgs = DDGSSearchProvider(timeout=5)
        self.last_attempts: list[dict[str, object]] = []

    def search(self, query: str, limit: int = 5) -> list[SearchHit]:
        try:
            hits = self.ddgs.search(query, limit=limit)
        finally:
            # Preserve every route attempt in the run trace, including when
            # all free public backends fail or return no results.
            self.last_attempts = list(self.ddgs.last_attempts)
        return hits
