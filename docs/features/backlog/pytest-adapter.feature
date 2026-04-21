Feature: Pytest adapter — generate pytest test stubs

  The pytest adapter is the default and first framework adapter. It produces
  pytest-compatible test stubs with the following conventions:

  - **Function prefix**: `test_`
  - **Skip marker**: `@pytest.mark.skip(reason="not yet implemented")`
  - **Deprecated marker**: `@pytest.mark.deprecated`
  - **Parametrize marker**: `@pytest.mark.parametrize(...)` — rendered from
    Scenario Outline columns by the adapter
  - **Return type**: `-> None`
  - **Body**: `...` (Ellipsis)
  - **Docstring**: full Gherkin scenario text verbatim (Given/When/Then steps)

  All marker templates are supplied by the adapter (not hard-coded in core),
  keeping the core framework-agnostic.

  Status: BASELINED (2026-04-21)
