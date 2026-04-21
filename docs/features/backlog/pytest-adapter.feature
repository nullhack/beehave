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

  Rules (Business):
  - The pytest adapter generates flat test functions, not classes.
  - Stub files must be importable by pytest discovery.

  Constraints:
  - pytest must be installed in the environment; the adapter does not enforce this.

  Rule: Generate standard pytest stubs
    As a pytest user
    I want beehave to generate test functions that pytest collects out of the box
    So that I can run `pytest` immediately after sync

    @id:c7d8e9f0
    Example: Basic pytest stub structure
      Given a `.feature` Example with `@id:deadbeef`
      When beehave sync runs with the pytest adapter
      Then the generated function is named `test_<feature_slug>_deadbeef`,
        has `@pytest.mark.skip(reason="not yet implemented")`,
        a docstring with the scenario text, `-> None`, and a body of `...`

    @id:d8e9f0a1
    Example: Deprecated pytest stub
      Given a `.feature` Example tagged with `@deprecated`
      When beehave sync runs with the pytest adapter
      Then the generated function also has `@pytest.mark.deprecated`

  Rule: Generate pytest parametrized stubs for Scenario Outlines
    As a pytest user with Scenario Outlines
    I want `@pytest.mark.parametrize` generated automatically
    So that I don't have to write pytest-specific parameter wiring

    @id:e9f0a1b2
    Example: Two-column Scenario Outline
      Given a `.feature` Scenario Outline with columns `name` and `email`
      When beehave sync runs with the pytest adapter
      Then the generated function has a parameter list `(name, email)` and
        a `@pytest.mark.parametrize` decorator with the example row values

    @id:f0a1b2c3
    Example: One-column Scenario Outline
      Given a `.feature` Scenario Outline with one column `role`
      When beehave sync runs with the pytest adapter
      Then the generated function has a single parameter `role` and
        a `@pytest.mark.parametrize` decorator with the example row values
