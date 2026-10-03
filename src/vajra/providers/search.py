from __future__ import annotations

from typing import Protocol

from vajra.models import SearchHit


class SearchProvider(Protocol):
    name: str

    def search(self, query: str, limit: int = 5) -> list[SearchHit]: ...


class DDGSSearchProvider:
    name = "ddgs"

    def health(self) -> tuple[str, str]:
        try:
            import ddgs  # noqa: F401
        except ImportError:
            return "unavailable", "Install the optional search provider with: pip install -e '.[search]'"
        return "configured", "DDGS library is installed; network health is verified only when a search runs."

    def search(self, query: str, limit: int = 5) -> list[SearchHit]:
        try:
            from ddgs import DDGS
        except ImportError as exc:
            raise RuntimeError("Search provider unavailable: install with pip install -e '.[search]'") from exc
        try:
            rows = DDGS(timeout=12).text(query, max_results=max(1, min(limit, 10)), backend="auto")
        except Exception as exc:
            raise RuntimeError(f"DDGS search failed: {type(exc).__name__}: {exc}") from exc
        hits = []
        for row in rows or []:
            url = str(row.get("href") or row.get("url") or "").strip()
            if not url:
                continue
            hits.append(SearchHit(url=url, title=str(row.get("title") or ""),
                                  snippet=str(row.get("body") or row.get("snippet") or ""),
                                  publisher=str(row.get("source") or ""), provider=self.name))
        return hits

