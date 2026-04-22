Feature: pytest-adapter — built-in adapter for the pytest framework

  Implements the adapter contract for pytest. Supplies the pytest-specific stub conventions used
  by sync-create, sync-update, and parameter-handling when pytest is the active framework.

  Status: BASELINED (2026-04-22)

  Rules (Business):
  - All generated pytest stubs are immediately runnable with pytest without modification

  Constraints:
  - Skip marker: @pytest.mark.skip(reason="not yet implemented")
  - Deprecated marker: @pytest.mark.deprecated
  - Parametrize: @pytest.mark.parametrize(...)
  - Function prefix: test_; return type: -> None; body: ...

  Rule: Pytest stub conventions
    As a developer
    I want generated pytest stubs to follow pytest conventions exactly
    So that pytest discovers and reports them correctly without any manual editing

    @id:128ddfaf
    Example: Generated stub has pytest skip marker
      Given a new Example in a .feature file
      When beehave sync generates the stub with the pytest adapter
      Then the function is decorated with @pytest.mark.skip(reason="not yet implemented")

    @id:4173073d
    Example: Generated stub function name follows test_ prefix convention
      Given a new Example with @id a1b2c3d4 in feature "honey-flow"
      When beehave sync generates the stub with the pytest adapter
      Then the function is named test_honey_flow_a1b2c3d4

    @id:342eff46
    Example: Generated stub has -> None return type annotation
      Given a new Example in a .feature file
      When beehave sync generates the stub with the pytest adapter
      Then the function signature ends with -> None

    @id:9221fd27
    Example: Generated stub body is Ellipsis
      Given a new Example in a .feature file
      When beehave sync generates the stub with the pytest adapter
      Then the function body is a single ... (Ellipsis) statement

    @id:56526c2a
    Example: Generated stub docstring contains full Gherkin step text
      Given an Example with Given/When/Then steps in a .feature file
      When beehave sync generates the stub with the pytest adapter
      Then the function docstring contains all Given, When, and Then lines verbatim

  Rule: Pytest deprecated marker
    As a developer
    I want beehave to add the deprecated marker to stubs for @deprecated Examples
    So that pytest marks those tests as deprecated automatically

    @id:fc7dc521
    Example: Deprecated stub has @pytest.mark.deprecated decorator
      Given an Example tagged @deprecated in a .feature file
      When beehave sync updates the stub with the pytest adapter
      Then the function is decorated with @pytest.mark.deprecated

    @id:24841ef4
    Example: Non-deprecated stub does not have the deprecated decorator
      Given an Example with no @deprecated tag
      When beehave sync generates the stub with the pytest adapter
      Then @pytest.mark.deprecated is absent from the function decorators

  Rule: Pytest file header
    As a developer
    I want the generated test file to have a valid pytest import header
    So that the file is valid Python and pytest can collect it without errors

    @id:9e7d16ec
    Example: Generated test file has pytest import
      Given a new Rule block requiring a new test file
      When beehave sync creates the file with the pytest adapter
      Then the file begins with import pytest
