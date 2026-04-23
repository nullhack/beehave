Feature: Sync Create — generate new test stubs
Status: BASELINED (2026-04-23)

`beehave sync` generates new test stubs for Gherkin Examples that have an
`@id` tag but no corresponding test function. Each stub follows the adapter's
template and contains the full Gherkin steps as a docstring.

Rule: Stub function structure

  @id:7e40f427
  Example: Stub function naming convention
    Given a `.feature` file "login" with an Example tagged `@id:a1b2c3d4`
    And no existing test for this Example
    When beehave sync runs
    Then a function named `test_login_a1b2c3d4` is generated

  @id:dbb0fbed
  Example: Stub contains skip marker from adapter template
    Given the pytest adapter is active
    And an unstubbed Example
    When beehave sync runs
    Then the stub function has `@pytest.mark.skip(reason="not yet implemented")`

  @id:ca473145
  Example: Stub docstring contains full Gherkin steps
    Given an Example with Given/When/Then steps
    When beehave sync runs
    Then the stub's docstring contains the steps verbatim

  @id:663d7f9c
  Example: Stub has None return type and Ellipsis body
    Given an unstubbed Example
    When beehave sync runs
    Then the stub function has `-> None` return type
    And the body is `...` (Ellipsis)

Rule: File layout follows Rule blocks

  @id:0951295f
  Example: One test file per Rule block
    Given a `.feature` file "login" with two Rule blocks
    When beehave sync runs
    Then two test files are generated under `tests/features/login/`

  @id:b0bdfa35
  Example: Rule slug determines file name
    Given a Rule named "Login validation"
    When beehave sync runs
    Then a file `login_validation_test.py` is created

Rule: Markers come from the adapter

  @id:8cb2dd6a
  Example: Markers are not hard-coded in core
    Given the pytest adapter provides skip and deprecated marker templates
    When beehave sync runs
    Then the generated stubs use the adapter-provided markers
