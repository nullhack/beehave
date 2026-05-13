Feature: Comb Construction

  Background:
    Given the colony has "Italian" genetics

  Rule: Comb building

    Scenario: worker builds a hexagonal cell
      Given a worker bee assigned to comb duty
      When the bee secretes <amount> milligrams of wax
      Then a new hexagonal cell is added to the comb
      And the cell wall is "beeswax"

  Rule: Brood management

    Background:
      Given the brood comb has 0 eggs

    Scenario: queen lays egg in cell
      Given a fertilized queen bee
      And an empty cell in the brood comb
      When the queen lays a <kind> egg
      Then the cell contains a <kind> egg

    Scenario Outline: nursery temperature regulation
      Given the ambient temperature is <ambient> degrees
      When <workers> bees cluster around the brood
      Then the brood temperature reaches <target> degrees

      Examples:
        | ambient | workers | target |
        | 28      | 20      | 35     |
        | 40      | 15      | 35     |
