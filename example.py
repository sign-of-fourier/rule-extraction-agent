"""Example: run the rule extraction agent on a sample SLA document."""

from rule_extraction_agent import extract_rules_from_document

SAMPLE_DOCUMENT = """
CLOUD SERVICE AGREEMENT – Service Level Agreement (SLA)
Effective Date: 2024-01-01

Section 1 – Availability

1.1  The provider must maintain a monthly uptime of 99.9% for all production
     services, measured from the first day of each calendar month.

1.2  Scheduled maintenance windows must not exceed 4 hours per month and must
     be announced at least 72 hours in advance via the customer portal.

1.3  The provider must notify the customer within 15 minutes of detecting any
     outage affecting more than 5% of API requests in a rolling 5-minute window.

Section 2 – Incident Response

2.1  Critical incidents (P1) must be acknowledged within 15 minutes and resolved
     within 4 hours of first detection. A P1 incident is defined as complete
     service unavailability or data loss risk.

2.2  High-severity incidents (P2) must be acknowledged within 1 hour and
     resolved within 24 hours.

2.3  The on-call engineer must post a status update every 30 minutes during any
     active P1 or P2 incident until resolution.

2.4  A root-cause analysis (RCA) report must be delivered to the customer within
     5 business days of resolving any P1 incident.

Section 3 – Data Handling

3.1  Customer data must be encrypted in transit using TLS 1.2 or higher and at
     rest using AES-256 encryption.

3.2  The provider must not store customer data outside the geographic region
     specified in the customer's account settings, except for disaster recovery
     backups, which may reside in a secondary region within the same jurisdiction.

3.3  Backups must be performed every 24 hours and retained for a minimum of
     30 days. Backups older than 30 days should be deleted within 7 days of
     expiration.

3.4  Upon contract termination, the provider must purge all customer data within
     30 days and provide a written confirmation of deletion.

Section 4 – Security

4.1  The provider must conduct a third-party penetration test at least once per
     calendar year and make a summary report available to the customer upon request.

4.2  All provider personnel with access to customer data must complete security
     awareness training annually.

4.3  Multi-factor authentication must be enforced for all administrative access
     to systems that process or store customer data.

4.4  Any suspected security breach must be reported to the customer's designated
     security contact within 24 hours of discovery, regardless of whether the
     breach has been confirmed.

Section 5 – Support

5.1  The customer may submit support requests via the ticketing portal or
     designated Slack channel at any time.

5.2  Support responses for P1 issues must be provided 24 hours a day, 7 days a
     week. For P2 and lower, support hours are Monday through Friday, 09:00–18:00
     in the customer's local timezone.

5.3  The provider should assign a dedicated customer success manager to accounts
     with monthly spend exceeding $10,000.
"""

if __name__ == "__main__":
    print("Running rule extraction on sample SLA document...\n")
    rules = extract_rules_from_document(SAMPLE_DOCUMENT)
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
