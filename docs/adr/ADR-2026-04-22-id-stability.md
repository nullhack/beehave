# ADR: @id assignment, collision, and orphan policy

| Field | Value |
|-------|-------|
| **Date** | 2026-04-22 |
| **Feature** | id-generation |
| **Status** | Accepted |

## Context

**Question (D3):** What is the format for `@id` tags? How are generation collisions handled? What happens to a stub when its `@id` is edited or deleted?

From discovery (I1/I1a): beehave generates 8-char lowercase hex IDs via `secrets.token_hex(4)`. Human-assigned IDs (any non-empty string) are valid and respected. Only an empty `@id:` value is malformed and gets replaced. The stakeholder confirmed that project-wide uniqueness is required — stubs are looked up by `@id` alone, so file-scoped uniqueness is insufficient. Duplicate `@id` found in files (always a hand-edit) → hard error, no safe resolution exists.

---

## Decision

`@id` values are 8-character lowercase hex strings. Once assigned, they are never replaced unless malformed (empty value or non-hex characters). Generation collisions trigger a silent retry. Uniqueness is enforced project-wide across all `.feature` files.

**Duplicate `@id` found in files** (hand-edited by developer): **always a hard error** — beehave cannot determine which stub to bind and must stop. This is never produced by beehave itself; its presence means a developer manually edited an `@id`.

**Edited or deleted `@id`**: the old stub becomes an orphan, subject to the `on_orphan` policy (configurable warn/error, default warn). A new `@id` is assigned and a new stub generated.

## Reason

Stable IDs are the sole link between an Example and its test stub. Any ID change breaks that link, orphaning the stub. Project-wide uniqueness prevents ambiguous stub lookups. Duplicate IDs are an unrecoverable ambiguity — beehave cannot guess which stub is canonical without risking silent data loss, so it must hard-error.

## Alternatives Considered

- **Sequential integers**: rejected — not stable across file renames or reordering; leaks ordering information
- **UUID v4 (full 32 hex chars)**: rejected — too verbose in `.feature` files; 8 hex chars gives 4 billion values, sufficient for any realistic project
- **Content-hash of step text**: rejected — changes when steps are edited, breaking the stability guarantee
- **File-scoped uniqueness**: rejected — beehave scans all feature files; project-wide uniqueness is required for unambiguous stub lookup
- **Configurable policy for duplicate @id**: rejected — there is no safe resolution strategy; hard error is the only honest response

## Consequences

- (+) Stubs survive Example reordering, file renames, and step text edits
- (+) `@id` in function name is the only lookup key needed — no path or title matching required
- (+) Duplicate ID is surfaced immediately as an error, never silently resolved
- (-) ID generation requires a full scan of all `.feature` files before assigning new IDs (to check uniqueness)
- (-) Malformed IDs must be detected and replaced — requires careful validation logic
- (-) Developer who manually edits an `@id` must resolve duplicates before beehave will run
