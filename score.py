"""
Score agent output against a silver labeled dataset.

Usage:
    python score.py                        # run agent + score vs silver
    python score.py --dry-run FILE.json    # score a saved JSON output without calling the agent

Matching: greedy bipartite, Jaccard similarity on normalized action text.
A pair is a match when similarity >= THRESHOLD. Threshold is intentionally low
(0.30) because the agent often paraphrases; tune with --threshold if needed.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

SILVER_PATH = Path(__file__).parent / "benchmarks" / "generic_life_underwriting_silver.json"
MATCH_THRESHOLD = 0.30


# ── Text similarity ────────────────────────────────────────────────────────────

def _tokens(text: str) -> set[str]:
    return set(re.sub(r"[^\w\s]", " ", text.lower()).split())


def _jaccard(a: str, b: str) -> float:
    sa, sb = _tokens(a), _tokens(b)
    union = sa | sb
    return len(sa & sb) / len(union) if union else 1.0


# ── Matching ───────────────────────────────────────────────────────────────────

def _greedy_match(
    gold: list[dict],
    extracted: list[dict],
    threshold: float,
) -> tuple[list[tuple[dict, dict, float]], list[dict], list[dict]]:
    """
    For each gold rule find the best unmatched extracted rule by action Jaccard.
    Returns (matches, missed_gold, hallucinated_extracted).
    """
    available = set(range(len(extracted)))
    matches: list[tuple[dict, dict, float]] = []
    missed: list[dict] = []

    for g in gold:
        best_sim, best_i = 0.0, -1
        for i in available:
            sim = _jaccard(g["action"], extracted[i]["action"])
            if sim > best_sim:
                best_sim, best_i = sim, i
        if best_i >= 0 and best_sim >= threshold:
            matches.append((g, extracted[best_i], best_sim))
            available.discard(best_i)
        else:
            missed.append(g)

    hallucinated = [extracted[i] for i in sorted(available)]
    return matches, missed, hallucinated


# ── Scoring ────────────────────────────────────────────────────────────────────

def run_score(gold: list[dict], extracted: list[dict], threshold: float = MATCH_THRESHOLD) -> dict:
    matches, missed_gold, hallucinated = _greedy_match(gold, extracted, threshold)

    tp = len(matches)
    fp = len(hallucinated)
    fn = len(missed_gold)
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall    = tp / (tp + fn) if (tp + fn) else 0.0
    f1        = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    mod_correct = sum(1 for g, r, _ in matches if r["modality"] == g["modality"])

    return dict(
        n_gold=len(gold),
        n_extracted=len(extracted),
        tp=tp, fp=fp, fn=fn,
        precision=precision, recall=recall, f1=f1,
        modality_accuracy=mod_correct / tp if tp else 0.0,
        matches=matches,
        missed_gold=missed_gold,
        hallucinated=hallucinated,
    )


# ── Reporting ──────────────────────────────────────────────────────────────────

def print_report(result: dict, gold: list[dict]) -> None:
    W = 60
    print(f"\n{'═'*W}")
    print(f"  RULE EXTRACTION BENCHMARK")
    print(f"{'═'*W}")
    print(f"  Gold rules        {result['n_gold']:>4}")
    print(f"  Extracted rules   {result['n_extracted']:>4}")
    print(f"  ──────────────────────")
    print(f"  True positives    {result['tp']:>4}  (matched to a gold rule)")
    print(f"  False positives   {result['fp']:>4}  (hallucinated — no gold match)")
    print(f"  False negatives   {result['fn']:>4}  (missed — no extracted match)")
    print(f"  ──────────────────────")
    print(f"  Precision         {result['precision']:>7.2f}")
    print(f"  Recall            {result['recall']:>7.2f}")
    print(f"  F1                {result['f1']:>7.2f}")
    print(f"  Modality accuracy {result['modality_accuracy']:>7.2f}  (of matched pairs)")

    # Per-modality recall and modality accuracy
    gold_by_mod = Counter(g["modality"] for g in gold)
    tp_by_mod   = Counter(g["modality"] for g, r, _ in result["matches"])
    mod_ok_by_mod = Counter(
        g["modality"] for g, r, _ in result["matches"] if r["modality"] == g["modality"]
    )

    print(f"\n  {'─'*W}")
    print(f"  {'Modality':<12} {'Gold':>5} {'Found':>6} {'Recall':>8} {'ModAcc':>8}")
    print(f"  {'─'*W}")
    for mod in ("must", "must_not", "may", "should"):
        n_gold = gold_by_mod.get(mod, 0)
        n_tp   = tp_by_mod.get(mod, 0)
        rec    = n_tp / n_gold if n_gold else 0.0
        n_ok   = mod_ok_by_mod.get(mod, 0)
        macc   = n_ok / n_tp if n_tp else 0.0
        print(f"  {mod:<12} {n_gold:>5} {n_tp:>6} {rec:>8.2f} {macc:>8.2f}")

    # Missed rules — most actionable signal
    if result["missed_gold"]:
        print(f"\n  MISSED RULES (false negatives) — {len(result['missed_gold'])}")
        for g in result["missed_gold"]:
            print(f"    [{g['modality']:<8}] {g['rule_id']}  {g['action'][:62]}")

    # Hallucinated rules
    if result["hallucinated"]:
        print(f"\n  HALLUCINATED RULES (false positives) — {len(result['hallucinated'])}")
        for r in result["hallucinated"]:
            print(f"    [{r['modality']:<8}] {r['rule_id']}  {r['action'][:62]}")

    # Modality mismatches in matched pairs
    mismatches = [(g, r) for g, r, _ in result["matches"] if r["modality"] != g["modality"]]
    if mismatches:
        print(f"\n  MODALITY MISMATCHES — {len(mismatches)}")
        print(f"  {'Gold ID':<10} {'Expected':<10} {'Got':<10}  Action (truncated)")
        print(f"  {'─'*W}")
        for g, r in mismatches:
            print(f"  {g['rule_id']:<10} {g['modality']:<10} {r['modality']:<10}  {g['action'][:40]}")

    print(f"\n{'═'*W}\n")


# ── Entry point ────────────────────────────────────────────────────────────────

def _rules_to_dicts(rules) -> list[dict]:
    """Convert Rule objects or plain dicts to plain dicts."""
    out = []
    for r in rules:
        if isinstance(r, dict):
            out.append(r)
        else:
            out.append(r.model_dump())
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        metavar="FILE",
        help="Score a previously saved JSON array of rules instead of running the agent",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=MATCH_THRESHOLD,
        help=f"Jaccard similarity threshold for a match (default {MATCH_THRESHOLD})",
    )
    parser.add_argument(
        "--silver",
        default=str(SILVER_PATH),
        help="Path to the silver/gold JSON label file",
    )
    args = parser.parse_args()

    gold: list[dict] = json.loads(Path(args.silver).read_text())

    if args.dry_run:
        extracted_raw = json.loads(Path(args.dry_run).read_text())
        extracted = _rules_to_dicts(extracted_raw)
    else:
        from rule_extraction_agent import extract_rules_from_document
        from sample_docs import GENERIC_LIFE_UNDERWRITING_DOCUMENT

        print("Running agent on generic life underwriting document…")
        rules = extract_rules_from_document(GENERIC_LIFE_UNDERWRITING_DOCUMENT)
        extracted = _rules_to_dicts(rules)
        print(f"Agent returned {len(extracted)} rules.\n")

        # Optionally save for later --dry-run reuse
        out_path = Path("benchmarks/last_run.json")
        out_path.write_text(
            json.dumps([r for r in extracted], indent=2, default=str)
        )
        print(f"(Saved to {out_path} for --dry-run reuse)\n")

    result = run_score(gold, extracted, threshold=args.threshold)
    print_report(result, gold)

    # Exit non-zero if F1 is below a basic bar, useful in CI
    if result["f1"] < 0.5:
        sys.exit(1)


if __name__ == "__main__":
    main()
