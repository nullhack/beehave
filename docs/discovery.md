# Discovery: beehave

> Append-only session synthesis log.
> Written by the product-owner at the end of each discovery session.
> Each block summarizes one session: what was learned, what entities were suggested, and which features were touched.
> Never edit past blocks — later blocks extend or supersede earlier ones.

---

## Session: 2026-04-21

### Summary

Session 1 established the full project scope for `beehave`: a framework-agnostic CLI and Python library that keeps Gherkin `.feature` files in sync with test stubs. The session covered all general questions (users, purpose, success/failure, out-of-scope), all cross-cutting concerns (framework selection, config, output modes, test identity, feature stage mapping), and per-feature Q&A for all 15 planned features. A same-day supplement corrected `deprecation-sync` cascade behavior (absolute, no override in v1) and defined `hatch` demo content (bee-themed, covers Feature/Rule/Example/Scenario Outline).

### Entities Added or Deprecated

| Action | Type | Name | Notes |
|--------|------|------|-------|
| Added | Noun | Feature file | Gherkin `.feature` file; single source of truth for requirements |
| Added | Noun | Example | Gherkin `Example:`/`Scenario:` block; unit that receives an `@id` and maps to one test stub |
| Added | Noun | Rule | `Rule:` block in a `.feature` file; maps to one test file in `tests/features/<slug>/` |
| Added | Noun | @id tag | 8-char lowercase hex tag (`@id:a1b2c3d4`); stable identity linking an Example to its test stub |
| Added | Noun | Test stub | Generated skipped test function `test_<feature_slug>_<id>` with Gherkin steps as docstring and `...` body |
| Added | Noun | Framework adapter | Pluggable component supplying stub template conventions per test framework |
| Added | Noun | Cache | JSON file at `.beehave_cache/features.json` tracking feature file state for incremental sync |
| Added | Noun | Feature slug | Snake-case identifier derived from a feature file's name; used as directory and function name prefix |
| Added | Noun | Rule slug | Snake-case identifier derived from a `Rule:` block title; used as the test file name |
| Added | Noun | Scenario Outline | Parameterized Gherkin example with a columns table; maps to a parametrized stub |
| Added | Noun | Orphan | A test stub whose `@id` no longer matches any Example in any `.feature` file |
| Added | Verb | nest | Bootstrap the canonical directory structure for a project |
| Added | Verb | sync | Assign IDs and reconcile test stubs with `.feature` files |
| Added | Verb | hatch | Generate demo `.feature` files |
| Added | Verb | assign_ids | Programmatic entry point to assign `@id` tags to untagged Examples |

### Features Touched

- `nest` — new feature: bootstraps canonical directory structure and pyproject.toml config injection
- `id-generation` — new feature: assigns stable `@id` tags to untagged or malformed Examples in place
- `status` — new feature: dry-run preview of what sync would change; Unix exit codes for CI
- `cache-management` — new feature: JSON cache for incremental sync, auto-rebuilds if stale or corrupted
- `template-customization` — new feature: user-defined stub templates via flag or config key
- `sync-create` — new feature: generates new skipped test stubs for Examples with no existing test
- `sync-update` — new feature: updates stub docstrings, function names, and deprecated markers on change
- `sync-cleanup` — new feature: warns on orphans, moves misplaced stubs, warns on deleted feature files
- `adapter-contract` — new feature: defines the interface all framework adapters must implement
- `pytest-adapter` — new feature: built-in adapter implementing the contract for pytest
- `parameter-handling` — new feature: parametrized stubs for Scenario Outlines; warns on column changes
- `unittest-adapter` — new feature: PARKED for v2; out of v1 scope
- `hatch` — new feature: generates bee-themed demo `.feature` files covering common Gherkin patterns
- `config-reading` — new feature: reads `[tool.beehave]` from `pyproject.toml` and applies defaults
- `deprecation-sync` — new feature: propagates `@deprecated` tags to stubs; absolute cascade, no override in v1
