"""Example: run the rule extraction agent on a life insurance underwriting guidelines document."""

from rule_extraction_agent import extract_rules_from_document
from sample_docs import LIFE_INSURANCE_UNDERWRITING_DOCUMENT

if __name__ == "__main__":
    print("Running rule extraction on life insurance underwriting guidelines...\n")
    rules = extract_rules_from_document(LIFE_INSURANCE_UNDERWRITING_DOCUMENT)
    print(f"Extracted {len(rules)} rules\n")
    print(f"{'ID':<10} {'Modality':<10} {'Actor':<30} {'Action'}")
    print("-" * 100)
    for r in rules:
        print(f"{r.rule_id:<10} {r.modality:<10} {r.actor[:29]:<30} {r.action[:55]}")
    print()

    # Break down by modality
    from collections import Counter
    counts = Counter(r.modality for r in rules)
    print("── Modality breakdown ──")
    for modality, count in sorted(counts.items()):
        print(f"  {modality:<12} {count}")

    print()
    print("── Full detail for first 3 rules ──")
    for r in rules[:3]:
        print()
        print(r.model_dump_json(indent=2))
