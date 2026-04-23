Feature: Pytest Adapter — generate pytest test stubs
Status: BASELINED (2026-04-23)

The pytest adapter provides pytest-specific marker templates and conventions
for stub generation.

Rule: Pytest skip marker

  @id:8cd24faa
  Example: Stub uses pytest skip marker
    Given the pytest adapter is active
    And an unstubbed Example
    When beehave sync runs
    Then the stub is decorated with `@pytest.mark.skip(reason="not yet implemented")`

Rule: Pytest deprecated marker

  @id:6bcbd28d
  Example: Deprecated Example uses pytest deprecated marker
    Given the pytest adapter is active
    And an Example tagged `@deprecated`
    When beehave sync runs
    Then the stub is decorated with `@pytest.mark.deprecated`

Rule: Pytest parametrize

  @id:751056a2
  Example: Scenario Outline uses pytest parametrize
    Given the pytest adapter is active
    And a Scenario Outline with columns
    When beehave sync runs
    Then the stub is decorated with `@pytest.mark.parametrize(...)`

Rule: Pytest function conventions

  @id:d2f344d0
  Example: Function prefix is test_
    Given the pytest adapter is active
    When beehave generates a stub
    Then the function name starts with `test_`

  @id:e89f492a
  Example: Return type is None
    Given the pytest adapter is active
    When beehave generates a stub
    Then the function signature includes `-> None`

  @id:c5b0db5d
  Example: Body is Ellipsis
    Given the pytest adapter is active
    When beehave generates a stub
    Then the function body is `...`
