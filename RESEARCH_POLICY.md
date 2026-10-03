# Research policy

1. Normalize and record the question and mode. Expand deterministic subqueries; do not imply an LLM planned them.
2. Search through the selected provider. Search titles/snippets are discovery hints, never evidence.
3. Validate and fetch candidate public URLs. Record failures and final URLs.
4. Extract bounded plain text and exact passages. Preserve dates and hashes where available.
5. Label excerpt claims `PARTIALLY_VERIFIED`: the text was found in a source, but truth/authority/independence remain unchecked.
6. Deep and forensic modes search for counterevidence and emit only heuristic conflict candidates; those candidates are not proven contradictions.
7. Audit offsets and citation IDs before writing the report. Keep provider failures visible.
8. Export the complete JSON trace and concise Markdown report so the same collected data can be replayed without network access.

The system does not promise zero hallucination. It avoids model-generated factual statements in the current core, but source text can itself be false or misleading. Human review and independent primary-source checks remain necessary.

