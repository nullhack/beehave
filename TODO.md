# Current Work

No feature in progress.

## Discovery Session 1 — COMPLETE (2026-04-21)

All general, cross-cutting, and per-feature questions answered and recorded.
All 14 v1 feature stubs updated and baselined. `unittest-adapter` parked for v2.

## Feature Stubs (docs/features/backlog/)

### Baselined (ready for Step 1 Stage 2 → Specification)
- `nest` — bootstrap canonical directory structure
- `hatch` — generate bee-themed example/demo feature files
- `config-reading` — read [tool.beehave] from pyproject.toml
- `id-generation` — assign @id tags to untagged Examples
- `sync-create` — generate new test stubs
- `sync-update` — update existing test stubs
- `sync-cleanup` — handle orphaned test stubs
- `status` — dry-run preview / CI gate
- `adapter-contract` — common framework adapter interface
- `pytest-adapter` — pytest stub generation
- `template-customization` — user-defined stub templates
- `cache-management` — incremental sync cache
- `deprecation-sync` — propagate @deprecated tags to stubs
- `parameter-handling` — Scenario Outline parametrization

### Parked (v2)
- `unittest-adapter` — unittest stub generation

## Next
Run @product-owner — load skill feature-selection and pick the next BASELINED feature from backlog.
