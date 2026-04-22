# ADR: Feature file write policy — @id tags only, surgical insertion

| Field | Value |
|-------|-------|
| **Date** | 2026-04-22 |
| **Feature** | id-generation, sync-create, sync-update |
| **Status** | Accepted |

## Decision

beehave writes to `.feature` files **only** to add `@id` tags to untagged Examples; all other content is read-only.

The write strategy is **surgical line insertion**: find the `Example:` (or `Scenario:`) line, insert `@id:<hex>` as a tag on the line immediately above it. The rest of the file is never touched. No full parse-and-reserialize round-trip.

## Reason

`.feature` files are the source of truth for requirements. Any write beyond `@id` assignment risks corrupting human-authored Gherkin. Surgical insertion guarantees zero formatting changes to surrounding content — indentation, comments, blank lines, and Unicode are all preserved byte-for-byte.

## Alternatives Considered

- **Full rewrite on sync**: rejected — destroys formatting, comments, and authoring intent
- **Parse and reserialize via gherkin-official**: rejected — the official parser produces an AST but has no canonical serializer; round-tripping would risk whitespace and comment loss
- **Separate ID sidecar file**: rejected — `@id` must be visible in the `.feature` file for traceability and portability
- **No write-back at all (IDs in sidecar)**: rejected — same reason as above

## Consequences

- (+) Feature files remain byte-identical except for the inserted `@id` lines
- (+) beehave is safe to run on any project; zero risk of formatting corruption
- (+) Implementation is simpler: line-level text manipulation, no AST serialization
- (-) Surgical insertion requires a reliable regex/line-scan to locate the correct `Example:` line, including edge cases (indentation, inline tags, `Scenario Outline:`)
- (-) Malformed `@id` tags (present but invalid) must be detected and replaced in-place using the same line-scan approach
