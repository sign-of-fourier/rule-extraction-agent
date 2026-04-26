# Benchmark Results

Evaluation of the rule extraction agent against a human-labeled silver dataset.

## Dataset

**Document:** Generic Life Insurance Underwriting Guidelines (synthetic, 6 sections, 29 clauses)
**Silver labels:** `benchmarks/generic_life_underwriting_silver.json` — 29 rules hand-labeled using the `Rule` schema (actor, condition, action, modality, exception, confidence, section_id).

This document was chosen deliberately as an **out-of-domain test** — the agent was developed and initially tested against a cloud SLA document. Life insurance underwriting uses completely different vocabulary, actors, and rule structures, making it a reasonable proxy for generalization.

## Results (run 2026-04-26)

| Metric | Score |
|---|---|
| Gold rules | 29 |
| Extracted rules | 33 |
| True positives | 28 |
| False positives | 5 |
| False negatives | 1 |
| **Precision** | **0.85** |
| **Recall** | **0.97** |
| **F1** | **0.90** |
| **Modality accuracy** | **1.00** |

### Per-modality breakdown

| Modality | Gold | Found | Recall | Modality acc |
|---|---|---|---|---|
| must | 12 | 12 | 1.00 | 1.00 |
| must_not | 5 | 5 | 1.00 | 1.00 |
| may | 9 | 8 | 0.89 | 1.00 |
| should | 3 | 3 | 1.00 | 1.00 |

## What the numbers mean

**Recall (0.97)** is the most important signal for this use case: the agent found 28 of 29 labeled rules. The one miss (RULE_029, reinstatement clause) was actually extracted — the scorer failed to match it because the gold label uses a short action (`"reinstate coverage"`) while the agent produced a verbose version, and the Jaccard similarity fell below the 0.30 matching threshold.

**Modality accuracy (1.00)** is the cleanest result: every rule the agent found was classified with the correct obligation strength (must / must_not / may / should). This is non-trivial — must_not rules especially require distinguishing negation from permission.

**The 5 false positives are not hallucinations.** Each corresponds to a real rule in the document. They are duplicate extractions produced by chunk overlap: when a sentence lands near a chunk boundary it gets extracted twice, and if the two versions phrase the action differently enough, the deduplicator lets both through and the scorer can only consume one as a TP. The rules in question: preferred non-tobacco class offer, standard tobacco class assignment, foreign travel assessment, postpone/decline for instability, and reinstatement.

## Known scorer limitations

- **Matching is Jaccard on action text only** with a 0.30 threshold. Verbose-vs-terse paraphrases of the same action can fall below it. The missed RULE_029 is an example.
- **No SLA gold file exists yet**, so there is no direct comparison to quantify domain bias. Adding one would let you measure whether the agent performs materially differently on familiar vs. unfamiliar domains.
- **Single run** — LLM outputs are stochastic. Results should be averaged across multiple runs before drawing strong conclusions.

## Reproduction

```bash
source .venv/bin/activate
python score.py                           # run agent + score
python score.py --dry-run benchmarks/last_run.json   # rescore saved output
python score.py --threshold 0.20          # loosen match threshold
```

The scorer saves agent output to `benchmarks/last_run.json` after each live run so you can re-score with different thresholds without a new API call.
