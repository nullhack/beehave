# ADR: Error vs. warn policy for deletions, duplicates, and malformed config

| Field | Value |
|-------|-------|
| **Date** | 2026-04-22 |
| **Feature** | sync-cleanup, id-generation, config-reading |
| **Status** | Accepted |

## Decision

Conditions that are **recoverable or informational** produce warnings (exit 0); conditions that are **unrecoverable or data-destructive** produce errors (exit non-zero). The warn/error threshold for deleted `.feature` files and duplicate `@id` values is configurable in `[tool.beehave]`.

## Reason

Unanswered gap A1 from scope_journal.md. Defaulting to warn-only for deletions and duplicates keeps beehave non-blocking in normal developer workflows while allowing CI pipelines to tighten the policy via config. Malformed `pyproject.toml` and invalid Gherkin are always errors because beehave cannot proceed without valid input.

## Alternatives Considered

- **Always error on any anomaly**: rejected — too aggressive; breaks developer workflow on partial migrations
- **Always warn, never error**: rejected — CI pipelines need a way to gate on drift; configurable threshold is the right balance
- **Separate `--strict` flag**: considered but deferred — config key is sufficient for v1; a flag can be added later

## Consequences

- (+) Default behavior is non-blocking; developers can run beehave at any project state
- (+) CI pipelines can tighten policy via `pyproject.toml` without code changes
- (-) Two code paths per condition (warn vs. error) must be maintained
- (-) Gap A1 is partially resolved: malformed `pyproject.toml` → error; invalid Gherkin → error; read-only filesystem → error with clear message; deleted feature → configurable warn/error (default warn)

## Unresolved (escalate to PO before implementation)

- A2 (performance targets) and A4 (structured logging) remain unanswered. These do not block v1 feature implementation but should be resolved before the cache-management and status features are accepted.
