# Changelog

All notable changes to pytest-beehave will be documented in this file.

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
