# Current Work

Feature: auto-id-generation
Step: 4 (VERIFY)
Source: docs/features/in-progress/auto-id-generation.feature

## Progress
- [x] Step 2 ARCH: read all features + existing package files, write domain stubs
- [x] Step 3 TDD Loop: RED → GREEN → REFACTOR for each @id bug
  - [x] `@id:a7b5c493`: Existing non-hex @id is used as-is for stub naming and no new @id is added
  - [x] `@id:b8c6d504`: Two @id tags on one Example cause a hard error at startup
- [x] Quality gate: lint, static-check, 100% coverage

## Backlog
- `stub-creation` — bugs: Scenario Outline parametrized stub (@id:f3e1a290), Background docstring separator (@id:e5c3b271)
- `stub-updates` — bug: Background docstring separator (@id:d6a4f382)

## Next
Run @reviewer — verify feature auto-id-generation at Step 4 (re-review after OC-1/nesting fix in _count_preceding_id_tags)
