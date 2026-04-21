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

  Rules (Business):
  - Stubs are generated only for Examples with an `@id` tag and no matching test.
  - One test file per Rule; test files live under `tests/features/<feature_snake>/`.
  - The adapter template decides the exact syntax of every marker.

  Constraints:
  - The existing file system layout (especially test files not matching the mapping)
    is never altered beyond creating new files and appending to existing ones.

  Rule: Generate new stubs for untested Examples
    As a developer adding new acceptance criteria
    I want a test stub created automatically for each new Example
    So that I only need to fill in the implementation body

    @id:d4e5f6a7
    Example: Single new Example in a new Rule
      Given a `.feature` file with one Example tagged `@id:abc12345`
        and no existing test files
      When beehave sync runs
      Then a new file `tests/features/<feature_snake>/<rule_slug>_test.py`
        is created containing one function `test_<feature_slug>_abc12345`

    @id:e5f6a7b8
    Example: Multiple new Examples in an existing file
      Given a `.feature` file with three new Examples and one existing test file
        with two old Examples
      When beehave sync runs
      Then the existing test file is appended with three new functions, one
        per new Example, preserving the old functions unchanged

    @id:f6a7b8c9
    Example: Stub body is Ellipsis
      Given beehave creates a new test stub
      Then the function body contains only `...` (Ellipsis, not `pass`)

  Rule: Generate parametrized stubs from Scenario Outlines
    As a developer using Scenario Outlines with table data
    I want the adapter to generate a native parametrize declaration
    So that I don't have to write framework-specific test loops by hand

    @id:a7b8c9d0
    Example: Scenario Outline with two columns
      Given a `.feature` file containing a Scenario Outline with columns
        `name` and `email`
      When beehave sync runs
      Then the generated stub function has a parametrize marker with the
        two column names as parameters, supplied by the adapter template

    @id:b8c9d0e1
    Example: Scenario Outline with no Examples table
      Given a `.feature` file containing a Scenario Outline without an
        `Examples:` table
      When beehave sync runs
      Then a standard non-parametrized stub is generated and a warning is
        emitted that the table is missing

  Rule: Deduplicate by @id
    As a developer who might accidentally trigger sync twice
    I want existing test stubs to never be duplicated
    So that I don't end up with multiple functions for the same Example

    @id:c9d0e1f2
    Example: Re-running sync does not duplicate stubs
      Given a `.feature` file with one Example whose `@id` already matches a
        test function name
      When beehave sync runs again
      Then no new test functions are created for that Example
