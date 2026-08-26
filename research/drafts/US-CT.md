# Connecticut hand-encoding draft

**Status:** Unreviewed research draft. Not a released ruleset.  
**Authority:** Conn. Pub. Act No. 26-14, § 10 (effective October 1, 2026).  
**Source record:** `US-CT-PA-26-14-20260826`.

## Candidate: baseline retention limit

The act states that ALPR data held by a public agency or its contracted private vendor must not be retained for more than 21 days, subject to enumerated exceptions. This is a candidate `retention` prohibition.

```jsonc
{
  "id": "CT-RET-001",
  "rule_type": "retention",
  "effect": "prohibited",
  "applies_when": { "field": "record.captured_jurisdiction", "op": "eq", "value": "US-CT" },
  "condition": { "field": "record.age_days", "op": "gt", "value": 21 },
  "grounding": {
    "provision_id": "PA 26-14 § 10(b)(2)(A)",
    "quote": "shall not be retained for a period in excess of twenty-one days"
  }
}
```

This fragment is deliberately **not evaluator-ready**. The same provision contains exceptions for court process, highway fees, active criminal matters with supervisory approval and documented case number, traffic analytics, later-offense evidence, and motor-vehicle-tax compliance. Several require state not represented by the current query schema. A released rule must encode or explicitly exclude each exception; it cannot publish the baseline prohibition alone.

## Candidate: immigration-purpose restriction

Section 10(d)(3) prohibits use or assistance in use for immigration-enforcement activity. The existing `query.purpose.code: immigration_enforcement` can represent part of this rule, but the statutory scope includes assistance and activity beyond a requester’s asserted purpose. Review must determine whether the data model can represent that scope without overclaiming.

## Required reviewer decisions

1. Confirm that § 10, rather than the repealed/incorrect prior citation, is the correct primary authority.
2. Identify a schema representation—or a documented coverage gap—for each retention exception.
3. Confirm whether the act’s October 1 effective date applies to every operative ALPR clause in § 10.
