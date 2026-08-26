# Oregon hand-encoding draft

**Status:** Unreviewed research draft. Not a released ruleset.  
**Authority:** 2026 Or. Laws ch. 77 (Enrolled S.B. 1516), §§ 4–5.  
**Source record:** `US-OR-SB-1516-ENROLLED-20260826`.

## Candidate: baseline use prohibition

Section 4(1) establishes a general prohibition and section 4(2) lists authorized uses. The current purpose enum does not represent every statutory category or the law’s jurisdictional equivalence tests. Therefore the baseline rule is recorded as a drafting target, not a release candidate.

## Candidate: retention limit

```jsonc
{
  "id": "OR-RET-001",
  "rule_type": "retention",
  "effect": "prohibited",
  "applies_when": { "field": "record.captured_jurisdiction", "op": "eq", "value": "US-OR" },
  "condition": { "field": "record.age_days", "op": "gt", "value": 30 },
  "grounding": {
    "provision_id": "2026 Or. Laws ch. 77 § 4(3)(a)",
    "quote": "may be retained for no more than 30 days after the captured license plate data is collected"
  }
}
```

The provision has a separate rule for data related to a court proceeding or ongoing criminal investigation and an audit-information carveout. The draft must not be frozen until those states are represented or listed as coverage gaps.

## Candidate: non-Oregon government access

Section 5(2) limits access for entities not created under Oregon law, while allowing a documented, purpose-limited exception. It requires fields for recipient legal origin, relevance, and ongoing/unrestricted access that do not exist in the present schema. This is a high-priority schema-review case, not an invitation to collapse “federal” into a legally complete proxy.

## Required reviewer decisions

1. Verify the exact passage/signing date before any legal-validity interval is assigned.
2. Review the relation between sections 4(1), 4(2), and 4(3) as a prohibition-plus-exceptions model.
3. Decide whether recipient legal origin requires a new closed field or an explicit v1 coverage gap.
