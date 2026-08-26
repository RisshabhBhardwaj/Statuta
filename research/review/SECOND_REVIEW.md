# Independent second-review protocol

This checklist applies to every artifact in `research/drafts/`. Completion authorizes neither a ruleset release nor a legal conclusion; it records the independent reading required before a draft can enter release review.

## Independence

- Reviewer name or stable pseudonym:
- Date reviewed:
- Jurisdiction and source record ID:
- I created my reading from the cited source before viewing the proposed encoding: yes / no
- Conflict or relevant affiliation disclosed:

## Required checks

For each candidate and each identified gap:

1. Verify that the quoted text appears in the registered normalized snapshot.
2. Verify that the quoted text supports the stated effect, operator, threshold, and scope.
3. Identify every exception, cross-reference, definition, effective-date clause, and remedy that changes the candidate’s meaning.
4. Mark each item: `agree`, `edit required`, `reject`, or `unencodable in v1`.
5. For an `edit required` or `reject` finding, cite the relevant provision and describe the change without relying on the first author’s framing.

## Required outcome

The reviewer must choose exactly one outcome for the jurisdiction:

- `advance_to_release_review` — all operative provisions in the declared scope are encoded or documented as coverage gaps;
- `research_more` — source history, definitions, cross-references, or schema fields remain unresolved; or
- `do_not_encode_v1` — the statute cannot be represented faithfully by the v1 DSL.

Review notes and any resulting rule changes must be committed with the candidate’s provenance. No unreviewed draft may be copied into `rulesets/`.
