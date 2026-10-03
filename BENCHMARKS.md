# Benchmarks

A deterministic scorer is available in [`benchmarks/README.md`](benchmarks/README.md). It checks exact evidence-span coverage against a versioned human-adjudicated corpus, quote/citation trace integrity, structural claim-to-evidence links, and recorded latency.

**Quality and comparative benchmarks have not been run.** No human-adjudicated corpus is present. Agent Reach's current capability/health interface is not equivalent to Vajra's report workflow, so the requested full-workflow comparison cannot be made fairly with the current integrations. Do not claim that Vajra is better or that these structural metrics establish factual accuracy.

For a future comparison, freeze a reviewed query set and gold evidence spans. Record code commit, retrieval date, query budget, provider/backends and versions, source access, configuration, machine, and raw traces. Measure exact evidence coverage and integrity, evidence diversity and independence, counterevidence recall, unsupported assertions after human entailment review, freshness, failure recovery, latency, and cost. Compare only systems given equivalent search/source access and budgets. Have human adjudicators review claims and conflicting evidence; vendor-generated answers are not gold labels without independent adjudication.
