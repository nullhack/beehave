# Changelog

All notable changes to pytest-beehave will be documented in this file.

## [v3.1.20260419] — Generative Augochlora — 2026-04-19

### Added
- feat(example-hatch): add `--beehave-hatch` flag to generate bee-themed example `.feature` files and demonstrate the plugin in one command

### Fixed
- fix(example-hatch): wrap `run_hatch()` call in `pytest_configure` with `try/except SystemExit` to produce clean error exit instead of `INTERNALERROR` crash

### Changed
- docs: add "See it in 2 minutes" demo section to README showing `--beehave-hatch` output and generated stubs
- chore: add `test-coverage` task to `pyproject.toml` for explicit coverage-only runs
- chore(skills): number SE Self-Declaration items 1–25 and add completeness check to reviewer skill

## [v3.0.20260419] — Foundational Apis — 2026-04-19

### Added
- feat(report-steps): surface BDD acceptance criteria in terminal (at `-v`) and pytest-html "Acceptance Criteria" column; scoped to `tests/features/`; independently configurable via `show_steps_in_terminal` / `show_steps_in_html`
- feat(living-docs): C4 Level 1 and Level 2 architecture diagrams (`docs/c4/`); living glossary (`docs/glossary.md`) derived from domain model and architectural decisions
- docs: add `docs/scientific-research/documentation.md` — Diátaxis, docs-as-code, blameless post-mortems, developer information needs

### Changed
- chore(sync): merge upstream v6.1.20260419 — new `living-docs` skill; updated `implementation`, `verify`, `git-release`, `create-skill` skills; `docs/post-mortem/` and `docs/c4/` directory stubs
- chore(workflow): restore and fix 10 damaged/missing files from v2 squash-merge gaps — `discovery.md`, `discovery_journal.md`, `architecture.md`, all agent files, scope/feature-selection/session-workflow skills, README `<@id>` format
- ci(release): add PyPI publish workflow triggered on `v*` tags via OIDC trusted publisher

## [v2.0.20260418] - Industrious Bombus - 2026-04-18

### Added
- feat(stub-creation): generate test stub files from Gherkin `.feature` files, with class-based layout per Rule block, Given/When/Then docstrings, and `@id` traceability
- feat(auto-id-generation): automatically write `@id` tags into `.feature` files for untagged Examples; enforce presence in CI (read-only mode)
- feat(deprecation-sync): sync `@pytest.mark.deprecated` markers from `.feature` `@deprecated` tags, including inheritance from parent Rule and Feature blocks
- feat(stub-updates): update stub docstrings when step text changes, rename functions when feature slug changes, mark non-conforming stubs, detect and mark orphaned stubs
- feat(features-dir-bootstrap): create canonical `backlog/`, `in-progress/`, `completed/` subfolders on first run; migrate loose `.feature` files to `backlog/`
- feat(plugin-hook): run stub sync as a `pytest_configure` hook so stubs are always up to date before collection

### Changed
- refactor: replace monolithic `syncer.py` with modular architecture (`feature_parser`, `stub_writer`, `stub_reader`, `sync_engine`, `bootstrap`, `reporter`, `models`)
- docs: rewrite README with colony/hive metaphors; waggle-dance how-it-works flow; hexagonal grid structure
