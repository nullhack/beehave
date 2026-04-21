# Current Work

Discovery Session 1 — Cross-cutting COMPLETE, Per-feature IN-PROGRESS
Next: Stakeholder to answer per-feature discovery questions for `nest`.

## Session State
- General questions: COMPLETE
- Cross-cutting questions: COMPLETE
- Per-feature discovery: IN-PROGRESS (starting with `nest`)

## Feature Stubs Created (docs/features/backlog/)
- `nest` — bootstrap canonical directory structure
- `hatch` — generate example/demo feature files
- `sync-create` — generate new test stubs
- `sync-update` — update existing test stubs
- `sync-cleanup` — handle orphan test stubs
- `status` — dry-run preview
- `id-generation` — assign @id tags
- `adapter-contract` — common adapter interface
- `pytest-adapter` — pytest stub generation
- `unittest-adapter` — unittest stub generation (future)
- `config-reading` — read [tool.beehave]
- `cache-management` — incremental sync cache
- `template-customization` — user-defined templates
- `deprecation-sync` — propagate @deprecated tags
- `parameter-handling` — Scenario Outline parametrization

## Splits Applied
- `framework-adapters` → `pytest-adapter` + `unittest-adapter`
- `sync` → `sync-create` + `sync-update` + `sync-cleanup`

## Next
Run @product-owner — continue per-feature discovery for `nest` after stakeholder answers.
