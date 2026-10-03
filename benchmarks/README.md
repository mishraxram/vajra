# Benchmark harness

`score.py` is a deterministic scorer for a versioned, human-adjudicated corpus and saved Vajra `research.json` traces. It measures exact gold-span coverage, trace citation/span integrity, structurally linked evidence, and recorded latency. It does not decide whether a source assertion is true or whether a passage semantically entails an abstract claim.

## Corpus format

Create a JSON file with a stable `corpus_id` and cases. `case_id` maps to a trace named `<case_id>.research.json`. Annotators should record literal evidence excerpts that answer the benchmark question, with adjudication notes/versioning maintained alongside the corpus. Do not use synthetic examples as quality ground truth.

```json
{
  "schema_version": "1",
  "corpus_id": "my-research-set-v1",
  "cases": [
    {
      "case_id": "question-001",
      "expected_evidence": ["literal, human-verified source excerpt"]
    }
  ]
}
```

Run from the project root:

```powershell
uv run --frozen python benchmarks/score.py --corpus path\to\corpus.json --traces path\to\reports --output work\benchmark-results.json
```

The scorer reports missing files and malformed input as failures. A zero-case corpus is valid but produces no coverage score. Save corpus, raw traces, output, code revision, provider versions, retrieval date, query budgets, and machine details together for reproducibility. Compare systems only when question sets, budgets, source access, dates, and evaluation rules are matched.

## Current status and limits

The harness is implemented and unit-tested, but **no quality benchmark has been run** because no human-adjudicated corpus exists in this project. There is no fair Agent Reach-vs-Vajra full-workflow comparison: Agent Reach's installed interface exposes platform-specific capabilities/health, not the same general report workflow. No score in this repository establishes truth, semantic entailment, source independence, provider cost, or superiority.
