# Current Work

Feature: auto-id-generation
Step: 2 (ARCH)
Source: docs/features/in-progress/auto-id-generation.feature

## Progress
- [ ] Step 2 ARCH: read all features + existing package files, write domain stubs
- [ ] Step 3 TDD Loop: RED → GREEN → REFACTOR for each @id bug
  - [ ] `@id:a7b5c493`: Existing non-hex @id is used as-is for stub naming and no new @id is added
  - [ ] `@id:b8c6d504`: Two @id tags on one Example cause a hard error at startup

## Backlog
- `stub-creation` — bugs: Scenario Outline parametrized stub (@id:f3e1a290), Background docstring separator (@id:e5c3b271)
- `stub-updates` — bug: Background docstring separator (@id:d6a4f382)

## Next
Run @software-engineer — load skill implementation and write architecture stubs for auto-id-generation bugs
