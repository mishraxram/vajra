from __future__ import annotations

import math
import re
from typing import TypedDict


class TextChunk(TypedDict):
    index: int
    start: int
    end: int
    estimated_tokens: int
    text: str


def chunk_text_sliding_window(text: str, *, max_tokens: int = 4_000,
                              overlap_tokens: int = 200) -> list[TextChunk]:
    """Split text near paragraph/sentence boundaries using a 4-char token estimate.

    The estimate is intentionally conservative and dependency-free; it is not a
    substitute for the tokenizer of a particular model. Offsets refer to the
    exact input string so chunks can be audited or resumed.
    """
    if max_tokens < 16 or overlap_tokens < 0 or overlap_tokens >= max_tokens:
        raise ValueError("max_tokens must be >= 16 and overlap_tokens must be smaller")
    if not text:
        return []
    width = max_tokens * 4
    overlap = overlap_tokens * 4
    chunks: list[TextChunk] = []
    start = 0
    while start < len(text):
        hard_end = min(len(text), start + width)
        end = hard_end
        if hard_end < len(text):
            floor = start + width * 3 // 4
            boundaries = list(re.finditer(r"\n\n|(?<=[.!?])\s+|\s+", text[floor:hard_end]))
            if boundaries:
                end = floor + boundaries[-1].end()
        if end <= start:
            end = hard_end
        value = text[start:end]
        chunks.append({"index": len(chunks), "start": start, "end": end,
                       "estimated_tokens": math.ceil(len(value) / 4), "text": value})
        if end >= len(text):
            break
        next_start = max(start + 1, end - overlap)
        # Keep the next chunk on a word boundary while maintaining overlap.
        while next_start < end and not text[next_start].isspace():
            next_start += 1
        start = min(next_start, end)
    return chunks
