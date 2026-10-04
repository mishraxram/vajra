from __future__ import annotations

import logging
from collections.abc import Iterable
from typing import Protocol

from vajra.models import SearchHit


class SearchProvider(Protocol):
    name: str

    def search(self, query: str, limit: int = 5) -> list[SearchHit]: ...


class DDGSSearchProvider:
    name = "ddgs"
    fallback_backends = ("duckduckgo", "bing", "brave")

    def __init__(self, timeout: int = 5):
        self.timeout = timeout
        self.last_attempts: list[dict[str, object]] = []

    def health(self) -> tuple[str, str]:
        try:
            import ddgs  # noqa: F401
        except ImportError:
            return "unavailable", "Install Vajra with its standard dependencies or install ddgs."
        return "configured", "Free public search is ready; no API key or paid account is required. Network is checked when a search runs."

    def search(self, query: str, limit: int = 5) -> list[SearchHit]:
        try:
            from ddgs import DDGS
        except ImportError as exc:
            raise RuntimeError("Search provider unavailable: install Vajra's standard dependencies.") from exc

        self.last_attempts = []
        engines = ("auto", *self.fallback_backends)
        errors: list[str] = []
        for index, backend in enumerate(engines):
            try:
                rows = DDGS(timeout=self.timeout).text(
                    query, max_results=max(1, min(limit, 10)), backend=backend
                )
                hits = self._hits(rows, backend)
                self.last_attempts.append({"backend": backend, "result_count": len(hits),
                                           "status": "ok" if hits else "empty"})
                if hits:
                    if index:
                        logging.getLogger("vajra.search").info(
                            "Search fallback succeeded using %s after %s", backend, engines[0]
                        )
                    return hits
            except Exception as exc:
                error_type = type(exc).__name__
                errors.append(f"{backend}: {error_type}")
                self.last_attempts.append({"backend": backend, "result_count": 0,
                                           "status": "error", "error_type": error_type})

        detail = ", ".join(errors) if errors else "all backends returned no results"
        raise RuntimeError(f"Search failed after trying {', '.join(engines)} ({detail})")

    def _hits(self, rows: object, backend: str) -> list[SearchHit]:
        hits: list[SearchHit] = []
        seen: set[str] = set()
        if not isinstance(rows, Iterable) or isinstance(rows, (str, bytes, dict)):
            return hits
        for row in rows:
            if not isinstance(row, dict):
                continue
            url = str(row.get("href") or row.get("url") or "").strip()
            if not url or url in seen:
                continue
            seen.add(url)
            hits.append(SearchHit(url=url, title=str(row.get("title") or ""),
                                  snippet=str(row.get("body") or row.get("snippet") or ""),
                                  publisher=str(row.get("source") or ""), provider=f"{self.name}:{backend}"))
        return hits
