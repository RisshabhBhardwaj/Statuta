# Research artifacts

This directory holds source registries and hand-authored encoding drafts used during corpus development.

## Status boundary

Nothing in `research/drafts/` is a released ruleset. Drafts are not loaded by the runtime, have not completed independent review, and must not be used to evaluate a real-world decision. They exist to make the author’s reading, unresolved questions, and required schema work inspectable before a release is considered.

Released corpus artifacts will live in `rulesets/` only after source verification, schema validation, independent review, and scenario testing. Until then, an absence from `rulesets/` means **not evaluated**, never permitted or unregulated.

## Source integrity

`research/sources/registry.json` identifies the immutable raw and normalized snapshots used for each draft. The raw source is the acquisition record; the normalized text is the review substrate. Both hashes must be reproduced before a draft can advance.
