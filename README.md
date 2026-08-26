# statuta

**Span-grounded, deterministic policy evaluation for automated license plate reader (ALPR) statutes.**

> **Status: foundations in progress.** `statuta` is not yet a legal research service, a compliance product, or a released corpus. It ships a deterministic evaluator for synthetic fixtures and a guarded production entry point, but no released statute corpus. Do not rely on it to assess any real-world access decision.

## Why this exists

Statutory constraints are commonly written as prose, while operational systems make access, disclosure, and retention decisions as data flows. `statuta` is an open rules-as-code project intended to make a narrow bridge between those forms: a released rule must be versioned, grounded to an exact statutory span, reviewable, and evaluated deterministically.

The design is deliberately conservative:

- A language model may propose rules offline; it never decides an access question at runtime.
- A released rule must carry source provenance and human-review metadata.
- Missing context and absent regulation are never silently treated as permission.
- Every eventual verdict will state its ruleset version, source coverage, and unresolved gaps.
- The project will never handle plate values, images, personal identifiers, or real query logs.

## Planned public artifacts

1. A schema-validated, span-grounded corpus of ALPR statutory rules.
2. A deterministic evaluator with explicit unknown-value and historical-version semantics.
3. Reproducible tests and a published evaluation of extraction and decision accuracy.

The first implementation milestone is hand-encoding and independently reviewing a small set of state statutes before any model-assisted extraction is attempted. If those statutes cannot be represented faithfully in a closed rule language, the project will publish a citation-and-annotation corpus instead of overstating what software can decide.

## Development

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```console
uv sync --all-groups
uv run ruff format --check .
uv run ruff check .
uv run ty check src
uv run pytest
```

Synthetic gold scenarios live in [gold/](gold/README.md). They are executable conformance fixtures, not legal conclusions. The public production entry point accepts only released, semantically validated rulesets; the currently tracked jurisdiction artifacts are explicitly unreviewed drafts.

## Security and scope

This repository is designed for public law and synthetic fixtures only. Please see [SECURITY.md](SECURITY.md) for responsible reporting. Issues that could produce a permissive evaluation error are treated as security issues.

## License

Code is licensed under [Apache-2.0](LICENSE). Any future corpus release will carry its own data license and provenance metadata.
