# statuta DSL v0.1

**Status:** Frozen for Phase 0 candidate work — 2026-08-26.

This is a deliberately small, closed rule representation for candidate artifacts. Any change requires an ADR and a schema-version decision. Candidate status does not make an artifact evaluable or reviewed.

## Runtime boundary

The runtime accepts only JSON predicates. It performs no I/O, network access, model call, clock read, or legal-text retrieval. Predicates return `true`, `false`, or `unknown`; missing data never becomes permission.

## Phase 1 evaluation semantics

The production entry point accepts only semantically validated `released` rulesets. The lower-level evaluator exists solely for content-free synthetic fixtures; it must not be pointed at a draft corpus.

Ruleset selection is deterministic and uses the query's `occurred_at`. A ruleset is selected only when that timestamp falls in its half-open legal-validity interval, `effective_at <= occurred_at < repealed_or_superseded_at` (or has no end), and its declared `actor`, `capture`, or `search` nexus is present in the context. A nexus match means that the corpus rule was selected for evaluation. It does **not** determine which jurisdiction's law legally governs a real-world activity or provide a comprehensive legal conclusion.

For each selected rule, `applies_when` and then `condition` are evaluated using three-valued logic. A false value does not fire the rule. An unknown value at either stage records an indeterminate coverage item. A conditional rule fires only when its condition is true and every requirement is true; an unknown requirement is indeterminate, while a false requirement means that conditional rule does not fire.

Resolution is fixed: a fired prohibition wins over every other effect; then a satisfied conditional rule; then permission; then indeterminate; then unregulated. Fired obligation rules accumulate their obligations alongside the verdict and do not themselves grant or deny permission. The verdict includes a deterministic resolution path plus selected rulesets, considered and fired rules, indeterminate reasons, and declared corpus coverage gaps.

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
