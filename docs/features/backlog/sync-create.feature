Feature: Sync-Create — generate new test stubs from `.feature` files

  As a developer writing BDD scenarios,
  I want beehave to automatically generate test stubs for every new Example that
  lacks a corresponding test,
  so that I don't have to write boilerplate test scaffolding by hand.

  Beehave generates one test file per `Rule:` block, placed at
  `tests/features/<feature_snake>/<rule_slug>_test.py`. Each stub is a top-level
  function named `test_<feature_slug>_<id>` (e.g. `test_login_a1b2c3d4`) with:
  - A skip marker sourced from the adapter template (not hard-coded in core)
  - A docstring containing the full Gherkin scenario text verbatim
    (Given/When/Then steps)
  - A `-> None` return type annotation
  - A body of `...` (Ellipsis, not `pass`)

  All markers (skip, deprecated, parametrize) are supplied by the adapter template,
  keeping the core framework-agnostic.

  Status: BASELINED (2026-04-21)
