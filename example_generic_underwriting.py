"""Example: run the rule extraction agent on the generic life insurance underwriting document."""

from rule_extraction_agent import extract_rules_from_document
from sample_docs import GENERIC_LIFE_UNDERWRITING_DOCUMENT

if __name__ == "__main__":
    print("Running rule extraction on generic life underwriting guidelines...\n")
    rules = extract_rules_from_document(GENERIC_LIFE_UNDERWRITING_DOCUMENT)
    print(f"Extracted {len(rules)} rules\n")
    print(f"{'ID':<10} {'Modality':<10} {'Actor':<20} {'Action'}")
    print("-" * 95)
    for r in rules:
        print(f"{r.rule_id:<10} {r.modality:<10} {r.actor[:19]:<20} {r.action[:55]}")
    print()
    print("── Full detail for first 3 rules ──")
    for r in rules[:3]:
        print()
        print(r.model_dump_json(indent=2))
