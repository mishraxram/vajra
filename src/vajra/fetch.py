from __future__ import annotations

import hashlib
import html
import re
import socket
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser

from vajra.models import FetchedSource
from vajra.security import validate_public_http_url

MAX_SOURCE_BYTES = 5 * 1024 * 1024
MAX_REDIRECTS = 5
TIMEOUT_SECONDS = 15
_DROP_ELEMENTS = {"script", "style", "noscript", "svg", "canvas", "iframe", "form", "template"}


class _PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.title_parts: list[str] = []
        self.metadata: dict[str, str] = {}
        self._drop_depth = 0
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_map = {str(k).lower(): str(v or "") for k, v in attrs}
        tag = tag.lower()
        if tag in _DROP_ELEMENTS:
            self._drop_depth += 1
            return
        if self._drop_depth:
            return
        if tag == "title":
            self._in_title = True
        if tag == "meta":
            key = (attrs_map.get("property") or attrs_map.get("name") or "").lower()
            content = attrs_map.get("content", "").strip()
            if key and content and key in {"og:title", "og:site_name", "author", "article:published_time", "date", "dc.date"}:
                self.metadata[key] = content[:500]
        if tag in {"p", "div", "br", "li", "h1", "h2", "h3", "h4", "blockquote", "article", "section", "tr"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in _DROP_ELEMENTS and self._drop_depth:
            self._drop_depth -= 1
            return
        if tag == "title":
            self._in_title = False
        if not self._drop_depth and tag in {"p", "div", "li", "h1", "h2", "h3", "h4", "blockquote", "article", "section", "tr"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._drop_depth:
            return
        text = re.sub(r"\s+", " ", data).strip()
        if not text:
            return
        if self._in_title:
            self.title_parts.append(text)
        self.parts.append(text + " ")


def _public_url(url: str) -> str:
    validate_public_http_url(url)
    return url


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        return None


def fetch_source(url: str, *, provider: str = "direct-fetch") -> FetchedSource:
    current = _public_url(url)
    opener = urllib.request.build_opener(_NoRedirect())
    headers = {"User-Agent": "VajraResearch/0.1 (+source-attributed research; no browser impersonation)",
               "Accept": "text/html, text/plain, application/xhtml+xml;q=0.9, application/xml;q=0.8"}
    body = b""
    content_type = ""
    for redirect_count in range(MAX_REDIRECTS + 1):
        request = urllib.request.Request(current, headers=headers, method="GET")
        try:
            response = opener.open(request, timeout=TIMEOUT_SECONDS)
        except urllib.error.HTTPError as exc:
            if exc.code in {301, 302, 303, 307, 308}:
                location = exc.headers.get("Location")
                if not location or redirect_count >= MAX_REDIRECTS:
                    raise RuntimeError("Redirect limit reached or Location missing") from exc
                current = _public_url(urllib.parse.urljoin(current, location))
                continue
            raise RuntimeError(f"Source fetch failed with HTTP {exc.code}") from exc
        with response:
            final = _public_url(response.geturl())
            content_type = response.headers.get_content_type().lower()
            if content_type not in {"text/html", "text/plain", "application/xhtml+xml", "application/xml"}:
                raise RuntimeError(f"Unsupported source content type: {content_type}")
            declared = response.headers.get("Content-Length")
            if declared and declared.isdigit() and int(declared) > MAX_SOURCE_BYTES:
                raise RuntimeError("Source exceeds the 5 MiB size limit")
            body = response.read(MAX_SOURCE_BYTES + 1)
            if len(body) > MAX_SOURCE_BYTES:
                raise RuntimeError("Source exceeds the 5 MiB size limit")
            current = final
            break
    else:
        raise RuntimeError("Redirect limit reached")

    encoding = "utf-8"
    if content_type:
        # Honor an explicit charset when available, but tolerate malformed declarations.
        try:
            charset = response.headers.get_content_charset()
            if charset:
                encoding = charset
        except LookupError:
            pass
    raw = body.decode(encoding, errors="replace")
    parser = _PageParser()
    if content_type != "text/plain":
        parser.feed(raw)
        parser.close()
        text = html.unescape(" ".join(parser.parts))
        text = re.sub(r"[ \t\f\v]+", " ", text)
        text = re.sub(r" *\n+ *", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        title = parser.metadata.get("og:title") or " ".join(parser.title_parts)
        author = parser.metadata.get("author", "")
        publisher = parser.metadata.get("og:site_name", "")
        published_at = parser.metadata.get("article:published_time") or parser.metadata.get("date") or parser.metadata.get("dc.date")
    else:
        text = raw.strip()
        title = ""
        author = ""
        publisher = ""
        published_at = None
    if not text:
        raise RuntimeError("Source contained no extractable text")
    digest = hashlib.sha256(body).hexdigest()
    source_id = hashlib.sha256(current.encode("utf-8")).hexdigest()[:24]
    return FetchedSource(source_id=source_id, url=current, final_url=current, title=html.unescape(title).strip()[:500], author=author[:300],
                         publisher=publisher[:300], published_at=published_at,
                         retrieved_at=datetime.now(timezone.utc).isoformat(), content_hash=digest,
                         text=text[:MAX_SOURCE_BYTES], source_type="web", provider=provider)


def select_passages(text: str, query: str, limit: int = 3) -> list[tuple[str, int, int, float]]:
    """Select exact text spans by lexical overlap; this is relevance ranking, not truth scoring."""
    tokens = {token.lower() for token in re.findall(r"[\w-]{3,}", query) if token.lower() not in _STOPWORDS}
    if not tokens:
        tokens = {token.lower() for token in re.findall(r"[\w-]{3,}", query)}
    candidates = []
    separators = list(re.finditer(r"(?<=[.!?])\s+(?=[A-Z0-9])|\n+", text))
    spans = []
    cursor = 0
    for separator in separators:
        if separator.start() > cursor:
            spans.append((cursor, separator.start()))
        cursor = separator.end()
    if cursor < len(text):
        spans.append((cursor, len(text)))
    for start, end in spans:
        raw = text[start:end]
        leading = len(raw) - len(raw.lstrip())
        trailing = len(raw.rstrip())
        passage = raw.strip()
        word_count = len(re.findall(r"[\w-]+", passage))
        if len(passage) < 50 or len(passage) > 1200 or word_count < 9:
            continue
        overlap = {term for term in tokens if re.search(rf"(?i)\b{re.escape(term)}\b", passage)}
        score = len(overlap) / max(len(tokens), 1)
        if score > 0:
            candidates.append((passage, start + leading, start + trailing, score))
    candidates.sort(key=lambda item: (-item[3], item[1]))
    selected = []
    seen = set()
    for item in candidates:
        key = item[0].casefold()
        if key in seen:
            continue
        seen.add(key)
        selected.append(item)
        if len(selected) >= limit:
            break
    return selected


_STOPWORDS = {"the", "and", "for", "with", "from", "that", "this", "what", "when", "where", "which", "does", "have", "about", "into", "evidence", "current", "latest", "research", "sources"}
