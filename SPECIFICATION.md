# statuta DSL v0.1

**Status:** Frozen for Phase 0 candidate work — 2026-08-26.

This is a deliberately small, closed rule representation for candidate artifacts. Any change requires an ADR and a schema-version decision. Candidate status does not make an artifact evaluable or reviewed.

## Runtime boundary

The runtime accepts only JSON predicates. It performs no I/O, network access, model call, clock read, or legal-text retrieval. Predicates return `true`, `false`, or `unknown`; missing data never becomes permission.

## Predicate grammar

- Combinators: `all`, `any`, `not`, `always`.
- Comparisons: `eq`, `ne`, `lt`, `lte`, `gt`, `gte`, `in`, `not_in`, `contains`, `is_null`, `is_not_null`.
- Domain operators: `authorization_at_least`, `jurisdiction_matches`, `any_recipient`.
- Field paths: only the versioned [field registry](schema/field-registry.json).

## Rule contract

Every rule requires an ID, a closed `rule_type`, an `effect`, scope and condition predicates, a literal quote, a half-open character span, the normalized source hash, and provenance. A conditional rule requires one or more machine-evaluable requirements. An obligation rule requires one or more obligations.

## Artifact states

`draft` rulesets are schema-valid research artifacts. They may have an unverified historical interval and may include hand-authored, unreviewed rules. They are never loaded by a public evaluator.

`released` rulesets require a verified effective date, independently reviewed rules, literal-span grounding verification, complete coverage accounting, and scenario tests. No released ruleset exists yet.

## Known v0.1 limits

The current context cannot faithfully express every statute’s court-process, vendor-contract, civil-action, data-aggregation, database-origin, or evidence-retention condition. Those provisions are coverage gaps unless and until a future schema version adds a reviewable, closed field for them.
