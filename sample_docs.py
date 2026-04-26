"""Sample documents for testing the rule extraction agent."""

GENERIC_LIFE_UNDERWRITING_DOCUMENT = """
Section 1 – Application and Eligibility
1.1 The insurer must receive a completed, signed life insurance application before underwriting begins.
1.2 The proposed insured must be between ages 18 and 75 at the time of application.
1.3 The owner must have an insurable interest in the proposed insured at the time of policy issue.
1.4 The insurer must not accept applications where the policy will be owned by a trust or business without disclosed beneficiaries and purpose.
1.5 The insurer may decline applications where the proposed insured is currently incarcerated or under criminal investigation.

Section 2 – Medical Underwriting Requirements
2.1 For face amounts up to 250,000 USD and ages 18–50, the insurer may use accelerated underwriting without a paramedical exam if the proposed insured has no significant health history.
2.2 For face amounts above 250,000 USD or ages over 50, the insurer must obtain a paramedical exam, blood profile, and urine specimen.
2.3 The insurer must obtain an attending physician statement when the proposed insured has a history of major cardiovascular disease, cancer, diabetes, or other serious chronic conditions.
2.4 The insurer must not offer accelerated underwriting to applicants who used tobacco or nicotine products in the past 12 months.
2.5 The insurer may order additional tests or reports at the underwriter's discretion if disclosed or discovered information suggests higher-than-average risk.

Section 3 – Risk Classification
3.1 The insurer must assign each approved policy to a risk class based on age, medical history, build, family history, and lifestyle factors.
3.2 The preferred non-tobacco class may be offered when the proposed insured has no significant medical history, meets build guidelines, and has not used tobacco or nicotine in the past 36 months.
3.3 Standard tobacco classes must be used for applicants who used tobacco or nicotine products within the past 12 months.
3.4 The insurer should consider table ratings or coverage limits for applicants with serious health conditions, hazardous occupations, or hazardous avocations such as skydiving, scuba diving beyond recreational limits, or private aviation.
3.5 The insurer must not approve coverage for applicants engaged in illegal activities that materially increase mortality risk.

Section 4 – Financial Underwriting and Amount Limits
4.1 The insurer must verify the reasonableness of the requested face amount relative to the proposed insured's income, assets, liabilities, and existing coverage.
4.2 For income replacement, the total in-force and applied-for coverage should generally not exceed 20–30 times annual earned income, based on age and underwriting guidelines.
4.3 The insurer must not issue policies where the premium payments are funded by prohibited stranger-originated life insurance (STOLI) or similar arrangements.
4.4 The insurer may require additional financial documentation, such as tax returns or business financial statements, for large face amounts or business-related insurance.
4.5 The insurer must ensure that the beneficiary designations are consistent with the stated purpose of coverage and applicable insurable interest laws.

Section 5 – Foreign Travel, Residence, and Occupation
5.1 The insurer should assess foreign travel and foreign residence based on destination, purpose, and duration when determining eligibility and risk class.
5.2 The insurer may postpone or decline coverage when the proposed insured plans extended stays in countries with high political instability, war, or significantly elevated health risks.
5.3 The insurer must consider occupational risk for applicants in hazardous occupations such as commercial fishing, mining, logging, or work at extreme heights.
5.4 The insurer may apply exclusions, ratings, or coverage limits to address specific travel, residence, or occupational hazards instead of declining outright, when permitted by underwriting guidelines.

Section 6 – Policy Issue, Contestability, and Reinstatement
6.1 The insurer must not issue the policy until all required underwriting evidence has been received and reviewed, and the proposed insured is determined to be insurable at an approved risk class.
6.2 The insurer must deliver the policy and collect the first premium before coverage becomes effective, unless temporary insurance has been issued under a separate receipt.
6.3 The policy must include a contestability period of not more than two years from the issue date, during which the insurer may rescind coverage for material misrepresentation or fraud, subject to applicable law.
6.4 After the contestability period, the insurer may only contest or rescind coverage in cases of proven fraud, as permitted by law.
6.5 If a policy lapses for nonpayment, the insurer may reinstate coverage within a specified period if all required premium is paid and the insured provides satisfactory evidence of insurability, subject to underwriting guidelines.
"""

SLA_DOCUMENT = """
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

LIFE_INSURANCE_UNDERWRITING_DOCUMENT = """
ACME LIFE INSURANCE COMPANY
Individual Life Insurance Underwriting Guidelines – Revision 14
Effective Date: 2025-01-01

────────────────────────────────────────────────────────────────
PART I – APPLICATION AND ELIGIBILITY
────────────────────────────────────────────────────────────────

Section 1 – Application Requirements

1.1  All applicants must complete a fully executed application form, including a
     signed authorization for release of medical information (HIPAA-compliant),
     before any underwriting review may begin.

1.2  The applicant must disclose all medical conditions, hospitalizations,
     surgeries, and prescribed medications within the past 10 years on the
     application. Failure to disclose known conditions constitutes material
     misrepresentation and may void the policy at any time after issuance.

1.3  For face amounts of $500,000 or more, the underwriter must order an
     Attending Physician Statement (APS) from each treating physician identified
     in the application before issuing a decision.

1.4  For face amounts of $1,000,000 or more, an independent medical examination
     (IME) conducted by a company-approved examiner must be completed and reviewed
     before a final underwriting decision is rendered.

1.5  Applications from applicants residing outside the United States must not be
     accepted unless the applicant holds a valid US visa with at least 12 months
     of remaining validity and has resided in the US for at least 2 continuous
     years at the time of application.

1.6  The underwriter should request financial documentation (most recent two years
     of tax returns and/or employer verification of income) when the applied-for
     face amount exceeds 20 times the applicant's stated annual income.

Section 2 – Age and Insurability Limits

2.1  The company must not issue new individual term life policies to applicants
     who are younger than 18 years of age or older than 75 years of age at the
     time of application.

2.2  Whole life and universal life policies must not be issued to applicants older
     than 80 years of age at the time of application.

2.3  Applicants aged 70 or older must complete a full paramedical examination,
     including an EKG and cognitive screening questionnaire, regardless of the
     applied-for face amount.

2.4  For applicants under age 18, a parent or legal guardian must sign the
     application as the policy owner, and the face amount must not exceed $50,000.

────────────────────────────────────────────────────────────────
PART II – MEDICAL UNDERWRITING
────────────────────────────────────────────────────────────────

Section 3 – Laboratory and Paramedical Requirements

3.1  For applicants aged 18–44 applying for face amounts of $250,000 or more,
     the underwriter must require a paramedical examination including blood
     pressure measurement, blood profile (CBC, CMP, lipid panel), and urinalysis.

3.2  For applicants aged 45–59 applying for any face amount, the underwriter
     must require a paramedical exam including the tests listed in 3.1 plus a
     PSA test (males) or CA-125 test (females), and a resting EKG.

3.3  For applicants aged 60 or older, the underwriter must require a full
     paramedical exam including all tests in 3.2, a treadmill stress EKG, and a
     chest X-ray.

3.4  Blood and urine specimens must be collected by a company-approved
     paramedical vendor and received at the approved laboratory within 48 hours
     of collection. Specimens arriving outside this window must be rejected and
     recollected.

3.5  Laboratory results must not be older than 90 days at the time the
     underwriting decision is rendered. If results are older than 90 days, the
     underwriter must order updated testing before issuing a decision.

Section 4 – Build and Blood Pressure Standards

4.1  Applicants whose body mass index (BMI) exceeds 40 must be rated a minimum
     of Table D (Standard Plus 100%) regardless of other health factors.

4.2  Applicants with a BMI between 35 and 40 should be reviewed for additional
     comorbidities (hypertension, diabetes, sleep apnea) and rated accordingly,
     with a minimum rating of Table B (Standard Plus 50%).

4.3  Applicants with a resting blood pressure reading above 160/100 mmHg on two
     or more separate readings must be declined unless the applicant provides
     documentation of treatment and readings below 150/95 mmHg within the past
     90 days.

4.4  Applicants with well-controlled hypertension (blood pressure consistently
     below 140/90 mmHg on medication) may be considered for Standard rates
     provided no other rated conditions are present.

Section 5 – Cardiovascular Conditions

5.1  Applicants with a history of myocardial infarction (heart attack) must not
     be offered coverage within 12 months of the event. After 12 months,
     eligibility is subject to full cardiac workup review.

5.2  Applicants with a history of coronary artery bypass graft (CABG) surgery
     may be considered for coverage no sooner than 24 months post-procedure,
     provided cardiac function has been documented as normal (EF ≥ 50%) by a
     treating cardiologist within the past 6 months.

5.3  Applicants with atrial fibrillation that is rate-controlled and documented
     as paroxysmal or persistent (not permanent) may be offered coverage at a
     rated table, subject to individual review; those with permanent atrial
     fibrillation must be individually reviewed by the Chief Medical Officer
     before any offer is extended.

5.4  Applicants with congestive heart failure at any stage must be declined.

5.5  The underwriter should obtain a current echocardiogram report (within the
     past 12 months) for any applicant with a known history of valvular heart
     disease before rendering a decision.

Section 6 – Cancer History

6.1  Applicants with an active malignancy (currently undergoing treatment or
     in active monitoring for recurrence) must be declined.

6.2  Applicants with a history of basal cell or squamous cell skin carcinoma
     that has been fully excised with clear margins may be considered for
     Standard rates provided there has been no recurrence within the past 2 years.

6.3  Applicants with a history of breast cancer must not be considered for
     coverage within 5 years of completing curative treatment. After 5 years,
     eligibility is subject to oncologist APS review and staging documentation.

6.4  Applicants with a history of prostate cancer (Gleason score ≤ 6, Stage I
     or II only) who have been in documented remission for at least 3 years may
     be offered coverage at a rated table. Higher Gleason scores or Stage III+
     require a minimum 7-year remission and Chief Medical Officer review.

6.5  Applicants with a history of melanoma must not be offered coverage within
     10 years of diagnosis regardless of staging, due to late-recurrence risk.

6.6  All cancer history cases that do not qualify for automatic decline or
     Standard issue under sections 6.1 through 6.5 must be referred to the
     Senior Underwriter for individual assessment.

Section 7 – Diabetes

7.1  Applicants with Type 1 diabetes must be individually assessed; insulin
     therapy alone does not disqualify an applicant, but current HbA1c must be
     below 8.5% and the applicant must have had no diabetes-related
     hospitalizations in the past 3 years to be considered for rated coverage.

7.2  Applicants with Type 2 diabetes controlled by diet or oral medication only,
     with HbA1c below 7.5% and no end-organ damage (nephropathy, retinopathy,
     neuropathy), may be offered Standard rates.

7.3  Applicants with Type 2 diabetes requiring insulin therapy must be rated a
     minimum of Table B, and an APS from the treating endocrinologist must be
     obtained before a decision is rendered.

7.4  Applicants with any form of diabetes who have a documented history of
     diabetic ketoacidosis (DKA) in the past 2 years must be declined.

Section 8 – Mental Health and Substance Use

8.1  Applicants with a history of a suicide attempt must not be offered coverage
     within 5 years of the most recent attempt. After 5 years, the underwriter
     must obtain an APS from the treating mental health provider.

8.2  Applicants with a current diagnosis of schizophrenia, schizoaffective
     disorder, or bipolar disorder Type I with a documented hospitalization in
     the past 2 years must be declined.

8.3  Applicants with a history of alcohol use disorder who have maintained
     documented sobriety for at least 2 continuous years and are actively
     participating in an outpatient support program may be considered for rated
     coverage. Those with sobriety of less than 2 years must be declined.

8.4  Applicants with a positive result for any Schedule I controlled substance
     on the urinalysis or on the application (excluding states where cannabis is
     legal and documented use is recreational) must be declined. Prescription
     opioid use without a documented current prescription must also result in
     a decline.

8.5  Applicants currently prescribed medication for depression or anxiety may be
     offered Standard rates provided the condition is documented as stable (no
     hospitalization, no medication change in the past 12 months) and the
     applied-for face amount does not exceed $1,000,000.

────────────────────────────────────────────────────────────────
PART III – RISK CLASSIFICATION AND RATING
────────────────────────────────────────────────────────────────

Section 9 – Rate Classes

9.1  The underwriter must assign each approved applicant to one of the following
     rate classes: Preferred Plus, Preferred, Standard Plus, Standard, Table A
     through Table P (each table representing an additional 25% of Standard
     premium), or Decline.

9.2  Preferred Plus classification requires: no tobacco use in the past 5 years,
     BMI between 18 and 28, blood pressure below 130/80 mmHg without medication,
     total cholesterol below 200 mg/dL, no family history of cardiovascular
     disease before age 60, and no rated medical conditions.

9.3  Applicants who have used any tobacco or nicotine product (including
     e-cigarettes and nicotine patches) within the past 12 months must be
     classified as a tobacco user and may not be offered Preferred or Preferred
     Plus rates, regardless of other health factors.

9.4  Applicants who self-report as non-tobacco users but test cotinine-positive
     on urinalysis must be reclassified as tobacco users. If the application has
     already been submitted as non-tobacco, the underwriter must decline the
     policy for misrepresentation.

9.5  When two or more ratable conditions are present, the underwriter must apply
     the most severe individual table rating and add half the table value of each
     additional ratable condition, rounding up to the nearest full table.

9.6  No policy may be issued at a table rating higher than Table P. Applicants
     whose combined table rating would exceed Table P must be declined.

Section 10 – Occupational and Avocational Hazards

10.1 Applicants employed in hazardous occupations (as defined in Appendix B of
     these guidelines) must be assessed for an occupational flat extra premium
     ranging from $2.50 to $10.00 per $1,000 of face amount, depending on the
     specific occupation and duties.

10.2 Applicants who participate in aviation as a pilot or co-pilot must be
     assessed for an aviation flat extra of $2.50 to $7.50 per $1,000 of face
     amount based on annual flight hours and aircraft type. Private pilots with
     fewer than 100 hours per year and no instrument-only operations may qualify
     for the low end of the range.

10.3 Applicants who engage in scuba diving below 100 feet, solo skydiving, base
     jumping, free solo climbing, or motorized racing must be assessed for an
     avocational flat extra premium. The underwriter should request a completed
     avocational questionnaire before determining the applicable flat extra.

10.4 Applicants who are active-duty military personnel assigned to a combat zone
     must not be issued a new policy while deployed; a war and aviation exclusion
     rider must be offered upon return from deployment if the application was
     pending at the time of deployment.

Section 11 – Foreign Travel and Residence

11.1 Applicants who have traveled to or resided in a country designated as a
     Level 3 or Level 4 travel advisory by the U.S. State Department within the
     past 12 months must have the travel documented and reviewed by the
     underwriter for potential flat extra or postponement.

11.2 Applicants who plan to reside outside the United States for more than
     6 consecutive months in the next 24 months must be individually assessed;
     coverage may be offered with a foreign residence exclusion rider or declined
     depending on the destination country's risk classification.

────────────────────────────────────────────────────────────────
PART IV – POLICY ISSUANCE AND POST-ISSUE
────────────────────────────────────────────────────────────────

Section 12 – Offers and Approval Authority

12.1 Underwriters at the Associate level may independently approve applications
     with a face amount up to $500,000 and a rate class no worse than Standard.

12.2 Applications with a face amount between $500,001 and $2,000,000 or a rate
     class of Table D or worse must be reviewed and co-signed by a Senior
     Underwriter before an offer is extended.

12.3 Applications with a face amount above $2,000,000 must be reviewed by the
     Chief Underwriting Officer and, for amounts above $5,000,000, also by the
     reinsurance treaty partner before a final offer is issued.

12.4 All decline decisions must include a written adverse action notice
     specifying the reason(s) for decline, the applicant's right to request
     reconsideration, and the specific regulatory disclosures required under
     applicable state law. The notice must be issued within 5 business days of
     the underwriting decision.

12.5 Conditional offers (offers contingent on additional information or
     examination results) must expire no later than 90 days from the date of
     the conditional offer letter. If conditions are not satisfied within 90
     days, the application must be closed and the applicant notified.

Section 13 – Contestability and Incontestability

13.1 The policy must include a 2-year contestability clause in accordance with
     applicable state law. During the contestability period, the company may
     investigate and, upon evidence of material misrepresentation, rescind the
     policy and refund premiums paid.

13.2 The underwriter must not deny a death claim solely on the basis of
     information that was available in the company's own records at the time of
     underwriting but was not considered during the original review.

13.3 After the 2-year contestability period has elapsed, the policy must be
     treated as incontestable, and claims must not be denied on the basis of
     misrepresentation except in cases of fraud.

Section 14 – Reinstatement

14.1 A lapsed policy may be reinstated within 3 years of the lapse date provided
     the insured submits a reinstatement application, evidence of insurability
     satisfactory to the underwriter, and payment of all overdue premiums plus
     applicable interest.

14.2 The underwriter must apply current underwriting guidelines to reinstatement
     applications; reinstatement must not be granted if the insured would be
     declined under current standards.

14.3 Reinstatement applications for policies that have been lapsed for more than
     12 months must be treated as new applications with full underwriting
     requirements, including new paramedical examination and laboratory work.
"""
