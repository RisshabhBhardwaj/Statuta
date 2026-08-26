# Virginia hand-encoding draft

**Status:** Unreviewed research draft. Not a released ruleset.  
**Authority:** Va. Code Ann. § 2.2-5517(D)–(F).  
**Source record:** `US-VA-2.2-5517-20260826`.

## Candidate: system-data retention

```jsonc
{
  "id": "VA-RET-001",
  "rule_type": "retention",
  "effect": "prohibited",
  "applies_when": { "field": "record.captured_jurisdiction", "op": "eq", "value": "US-VA" },
  "condition": { "field": "record.age_days", "op": "gt", "value": 21 },
  "grounding": {
    "provision_id": "Va. Code § 2.2-5517(E)",
    "quote": "System data shall be purged after 21 days of the date of its capture"
  }
}
```

This is not a complete rule. The same subsection provides a retention exception for ongoing investigations, prosecutions, and civil actions, with a detailed end condition. The query schema does not yet represent those distinctions. Audit-trail data has a different two-year rule and is a separate potential object type.

## Candidate: sharing restriction

Section 2.2-5517(F) prohibits sharing or dissemination to a database of another state, federal, private, or commercial entity but lists six exceptions. The present context can represent recipient type but not whether the recipient is a database, the listed legal purpose, discovery, subpoena, or maintenance/quality-assurance basis. No release candidate is proposed until those are resolved.

## Required reviewer decisions

1. Trace the effective-date and amendment history from session-law authority; the current code PDF is not sufficient for a historical validity interval.
2. Determine whether “system data” maps exactly to `record.kind: plate_read` or requires a broader data-kind representation.
3. Review all section (F) exceptions before creating a sharing rule.
