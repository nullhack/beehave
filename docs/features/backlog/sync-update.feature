Feature: Sync Update — update existing test stubs
Status: BASELINED (2026-04-23)

`beehave sync` updates existing test stubs when their corresponding Gherkin
Example has changed. It updates the docstring and function name but never
modifies the test body.

Rule: Docstring is re-rendered on Example change

  @id:539cf88b
  Example: Changed steps update the docstring
    Given an existing stub with a docstring
    And the corresponding Example's steps have changed
    When beehave sync runs
    Then the stub's docstring is updated to match the new steps

Rule: Function name updates on feature slug change

  @id:71cb4b18
  Example: Feature rename triggers function rename
    Given an existing stub named `test_login_a1b2c3d4`
    And the `.feature` file is renamed from "login" to "sign_in"
    When beehave sync runs
    Then the function is renamed to `test_sign_in_a1b2c3d4`

Rule: @deprecated marker is added or removed

  @id:70ab8602
  Example: Adding @deprecated tag adds the marker
    Given an existing stub without a deprecated marker
    And the corresponding Example gains `@deprecated`
    When beehave sync runs
    Then the deprecated marker from the adapter is added to the stub

  @id:f3e0cbc2
  Example: Removing @deprecated tag removes the marker
    Given an existing stub with a deprecated marker
    And the corresponding Example loses `@deprecated`
    When beehave sync runs
    Then the deprecated marker is removed from the stub

Rule: Test body is never modified

  @id:670fc55a
  Example: Developer code in the body is preserved
    Given an existing stub where the developer replaced `...` with test code
    When beehave sync runs
    Then the developer's test body is left completely unchanged

Rule: Scenario Outline column changes are warn-only

  @id:98eec312
  Example: Column change triggers warning
    Given an existing parametrised stub
    And the Scenario Outline gains a new column
    When beehave sync runs
    Then a warning is issued: "manual intervention required"
    And the parametrize decorator is NOT updated
