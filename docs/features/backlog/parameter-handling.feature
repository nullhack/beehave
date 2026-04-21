Feature: Parameter handling — manage parametrized stubs from Scenario Outlines

  Scenario Outlines with `Examples:` tables generate parametrized test stubs
  rather than flat functions. The adapter uses native framework conventions
  (e.g., `@pytest.mark.parametrize`) so that the parameters are handled
  idiomatically for the target test runner. The docstring preserves the raw
  template step text and the full Examples table.

  Status: DRAFT
