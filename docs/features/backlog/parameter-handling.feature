Feature: Parameter Handling — Scenario Outline parametrization
Status: BASELINED (2026-04-23)

Beehave renders Scenario Outline columns as framework-specific parametrised
stubs. Column changes after initial stub creation are warn-only.

Rule: Scenario Outline renders as parametrised stub

  @id:289d971d
  Example: Scenario Outline generates parametrised test
    Given a Scenario Outline with "username" and "password" columns
    And the pytest adapter is active
    When beehave sync runs
    Then the stub includes `@pytest.mark.parametrize` with the column data

Rule: Column changes after initial creation are warn-only

  @id:2ff2a0f5
  Example: New column triggers warning
    Given an existing parametrised stub for a Scenario Outline
    And a new column "email" is added to the Scenario Outline
    When beehave sync runs
    Then a warning is issued: "manual intervention required"
    And the parametrize decorator is NOT updated
