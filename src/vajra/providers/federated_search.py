from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from vajra.models import SearchHit
from vajra.providers.search import DDGSSearchProvider


class AgentReachExaSearchProvider:
    """Use Agent Reach's configured Exa MCP tool through mcporter."""

    name = "agent-reach-exa"
    timeout_seconds = 20

    def executable(self) -> str | None:
        return shutil.which("mcporter")

    def search(self, query: str, limit: int = 5) -> list[SearchHit]:
        executable = self.executable()
        if not executable:
            raise RuntimeError("mcporter is not installed")

        # Keep arbitrary user query text out of a shell command line. mcporter's
        # documented query=@path form reads the UTF-8 payload from a temp file.
        with tempfile.TemporaryDirectory(prefix="vajra-exa-") as temp_dir:
            query_path = Path(temp_dir) / "query.txt"
            query_path.write_text(query, encoding="utf-8")
            result = subprocess.run(
                [executable, "call", "--no-oauth", "exa.web_search_exa",
                 f"query=@{query_path}", f"numResults={max(1, min(limit, 10))}",
                 "--output", "json"],
                capture_output=True, text=True, timeout=self.timeout_seconds,
                check=False, shell=False,
            )
        if result.returncode != 0:
            raise RuntimeError(f"mcporter exited {result.returncode}")
        try:
            envelope = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError("mcporter did not return JSON") from exc

        hits: list[SearchHit] = []
        seen: set[str] = set()
        for block in envelope.get("content", []):
            if not isinstance(block, dict) or block.get("type") != "text":
                continue
            for title, url, snippet in self._parse_results(str(block.get("text", ""))):
                if url in seen:
                    continue
                seen.add(url)
                hits.append(SearchHit(url=url, title=title, snippet=snippet,
                                      publisher="", provider=self.name))
                if len(hits) >= max(1, min(limit, 10)):
                    return hits
        return hits

    @staticmethod
    def _parse_results(text: str) -> list[tuple[str, str, str]]:
        """Parse mcporter text blocks without treating highlights as evidence."""
        starts = list(re.finditer(r"(?m)^Title:\s*", text))
        parsed: list[tuple[str, str, str]] = []
        for index, match in enumerate(starts):
            end = starts[index + 1].start() if index + 1 < len(starts) else len(text)
            record = text[match.start():end]
            title_line = record.splitlines()[0]
            title = title_line.partition(":")[2].strip()
            url_match = re.search(r"(?m)^URL:\s*(https?://\S+)\s*$", record)
            if not url_match:
                continue
            highlight_match = re.search(r"(?ms)^Highlights:\s*\n(.*?)(?:\n---\s*$|\Z)", record)
            snippet = highlight_match.group(1).strip()[:12000] if highlight_match else ""
            parsed.append((title[:500], url_match.group(1), snippet))
        return parsed


class FederatedSearchProvider:
    """Combine Agent Reach's Exa search with DDGS and deduplicate URLs."""

    name = "agent-reach-exa+ddgs"

    def __init__(self) -> None:
        self.agent_reach = AgentReachExaSearchProvider()
        self.ddgs = DDGSSearchProvider()
        self.last_attempts: list[dict[str, object]] = []

    def search(self, query: str, limit: int = 5) -> list[SearchHit]:
        self.last_attempts = []
        results: list[SearchHit] = []
        seen: set[str] = set()
        for provider in (self.agent_reach, self.ddgs):
            try:
                hits = provider.search(query, limit=limit)
                for hit in hits:
                    if hit.url not in seen:
                        seen.add(hit.url)
                        results.append(hit)
                self.last_attempts.append({"backend": provider.name, "status": "ok" if hits else "empty",
                                           "result_count": len(hits)})
            except Exception as exc:
                self.last_attempts.append({"backend": provider.name, "status": "error",
                                           "result_count": 0, "error_type": type(exc).__name__})
        if not results:
            details = ", ".join(str(item["backend"]) + ":" + str(item["status"])
                                 for item in self.last_attempts)
            raise RuntimeError(f"All configured search providers failed or returned no results ({details})")
        return results[:max(1, min(limit * 2, 20))]
