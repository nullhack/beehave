# Current Work

Feature: stub-creation
Step: 2 (ARCH)
Source: docs/features/in-progress/stub-creation.feature

## Progress
- [ ] `@id:692972dd`: New stub is created with the correct function name
- [ ] `@id:a4c781f2`: New stub has skip marker not yet implemented
- [ ] `@id:f1a5c823`: New stub for a feature with no Rule blocks is a module-level function
- [ ] `@id:777a9638`: New stub body contains raise NotImplementedError
- [ ] `@id:bba184c0`: New stub body contains only raise NotImplementedError with no section comments
- [ ] `@id:edc964fc`: Test directory uses underscore slug not kebab-case
- [ ] `@id:38d864b9`: Stubs are not created for completed feature Examples
- [ ] `@id:f3e1a290` (@bug): Scenario Outline produces a parametrized stub
- [ ] `@id:db596443`: And and But steps use their literal keyword in the docstring
- [ ] `@id:17b01d7a`: Asterisk steps appear as "* <text>" in the docstring
- [ ] `@id:c56883ce`: Multi-line doc string attached to a step is included in the docstring
- [ ] `@id:2fc458f8`: Data table attached to a step is included in the docstring
- [ ] `@id:7f91cf3a`: Background steps appear as separate Background sections before scenario steps
- [ ] `@id:9a4e199a`: Scenario Outline stub uses raw template text and includes the Examples table
- [ ] `@id:e5c3b271` (@bug): Background steps are separated from scenario steps by a blank line in the docstring

## Backlog
- `stub-updates` — Status: BASELINED (2026-04-18); bug: Background docstring separator (@id:d6a4f382)
- `incremental-sync` — Status: BASELINED (2026-04-20); mtime+size cache in .beehave-cache/; 7 Rules, 20 Examples

## Completed
- `auto-id-generation` — accepted at Step 5 (2026-04-20); moved to docs/features/completed/; bug registered 2026-04-20: non-8-char @id uniqueness collision (@id:e9d7f615, GitHub #19)

## Next
Run @software-engineer — load skill implementation and begin Step 2 (Architecture) for stub-creation
