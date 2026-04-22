# ADR: Feature file write policy — @id tags only

| Field | Value |
|-------|-------|
| **Date** | 2026-04-22 |
| **Feature** | id-generation, sync-create, sync-update |
| **Status** | Accepted |

## Decision

beehave writes to `.feature` files **only** to add `@id` tags to untagged Examples; all other content is read-only.

## Reason

`.feature` files are the source of truth for requirements. Any write beyond `@id` assignment risks corrupting human-authored Gherkin, breaking stakeholder trust, and making beehave unsafe to run in CI.

## Alternatives Considered

- **Full rewrite on sync**: rejected — destroys formatting, comments, and authoring intent
- **Separate ID sidecar file**: rejected — breaks the one-file-per-feature contract and complicates tooling
- **No write-back at all (IDs in sidecar)**: rejected — `@id` must be visible in the `.feature` file for traceability

## Consequences

- (+) Feature files remain human-readable and diff-friendly
- (+) beehave is safe to run on any project without risk of data loss
- (-) beehave must parse and re-serialize Gherkin with exact whitespace preservation — non-trivial implementation constraint
- (-) Malformed `@id` tags must be detected and replaced in-place, requiring careful regex/AST handling
