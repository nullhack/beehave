# ADR: @id assignment and collision policy

| Field | Value |
|-------|-------|
| **Date** | 2026-04-22 |
| **Feature** | id-generation |
| **Status** | Accepted |

## Decision

`@id` values are 8-character lowercase hex strings; once assigned they are never replaced (unless malformed); collisions trigger a silent retry; uniqueness is enforced project-wide across all `.feature` files.

## Reason

Stable IDs are the sole link between an Example and its test stub. Any ID change breaks that link, orphaning the stub and losing the developer's test body. Project-wide uniqueness prevents ambiguous stub lookups.

## Alternatives Considered

- **Sequential integers**: rejected — not stable across file renames or reordering; leaks ordering information
- **UUID v4 (full 32 hex chars)**: rejected — too verbose in `.feature` files; 8 hex chars gives 4 billion values, sufficient for any realistic project
- **Content-hash of step text**: rejected — changes when steps are edited, breaking the stability guarantee
- **File-scoped uniqueness**: rejected — beehave scans all feature files; project-wide uniqueness is required for unambiguous stub lookup

## Consequences

- (+) Stubs survive Example reordering, file renames, and step text edits
- (+) `@id` in function name is the only lookup key needed — no path or title matching required
- (-) ID generation requires a full scan of all `.feature` files before assigning new IDs (to check uniqueness)
- (-) Malformed IDs must be detected and replaced — requires careful validation logic
