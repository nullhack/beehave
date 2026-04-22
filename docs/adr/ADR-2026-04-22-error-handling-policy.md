# ADR: Error vs. warn policy

| Field | Value |
|-------|-------|
| **Date** | 2026-04-22 |
| **Feature** | sync-cleanup, id-generation, config-reading |
| **Status** | Accepted |

## Context

**Question (A1/D6):** How should beehave behave when `pyproject.toml` is malformed, a `.feature` file has invalid Gherkin, or the filesystem is read-only? Which conditions warrant a hard error vs. a configurable warn/error?

Stakeholder decisions: malformed (present but invalid) `pyproject.toml` → hard error; absent `pyproject.toml` → use defaults, no error; invalid Gherkin → hard error; read-only filesystem → hard error. Deleted feature file and orphan stubs → configurable, default warn. Duplicate `@id` → hard error always, never configurable (see `ADR-2026-04-22-id-stability`). New config keys surfaced: `on_delete` and `on_orphan`.

---

## Decision

| Condition | Policy | Configurable? |
|-----------|--------|---------------|
| `pyproject.toml` absent | Use defaults, no error | No |
| `pyproject.toml` present but invalid TOML | Hard error | No |
| Invalid Gherkin syntax in `.feature` file | Hard error | No |
| Read-only filesystem (cannot write stubs or @id) | Hard error | No |
| Duplicate `@id` found across files | Hard error | No |
| Deleted `.feature` file (orphan feature directory) | Warn (default) or error | Yes — `on_delete` |
| Orphan stub (no matching `@id` in any feature) | Warn (default) or error | Yes — `on_orphan` |

## Reason

Conditions where beehave **cannot proceed correctly** are always hard errors — there is no safe partial result. Conditions that are **informational or recoverable** default to warn so beehave is non-blocking in normal developer workflows; CI pipelines can tighten the policy via config.

Absent `pyproject.toml` is explicitly not an error — the tool must work out of the box with zero config. Duplicate `@id` is a hard error because beehave cannot resolve the ambiguity without risking silent stub loss (see ADR-2026-04-22-id-stability).

## Alternatives Considered

- **Always error on any anomaly**: rejected — too aggressive; breaks developer workflow on partial migrations
- **Always warn, never error**: rejected — CI pipelines need a way to gate on drift; configurable threshold is the right balance
- **Configurable policy for duplicate @id**: rejected — no safe resolution exists; see id-stability ADR
- **Separate `--strict` flag**: considered but deferred — config keys are sufficient for v1; a flag can be added later

## Consequences

- (+) Default behavior is non-blocking; developers can run beehave at any project state
- (+) CI pipelines can tighten `on_delete` and `on_orphan` via `pyproject.toml` without code changes
- (+) Hard errors are predictable and documented — no surprise exits
- (-) Two code paths per configurable condition (warn vs. error) must be maintained
- (-) `on_delete` and `on_orphan` config keys must be added to the `config-reading` feature scope (PO to update)
