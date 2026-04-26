"""Example: run the rule extraction agent on a sample SLA document."""

from rule_extraction_agent import extract_rules_from_document
from sample_docs import SLA_DOCUMENT

if __name__ == "__main__":
    print("Running rule extraction on sample SLA document...\n")
    rules = extract_rules_from_document(SLA_DOCUMENT)
    print(f"Extracted {len(rules)} rules\n")
    print(f"{'ID':<10} {'Modality':<10} {'Actor':<25} {'Action'[:60]}")
    print("-" * 90)
    for r in rules:
        print(f"{r.rule_id:<10} {r.modality:<10} {r.actor[:24]:<25} {r.action[:50]}")
    print()
    print("── Full detail for first 3 rules ──")
    for r in rules[:3]:
        print()
        print(r.model_dump_json(indent=2))
