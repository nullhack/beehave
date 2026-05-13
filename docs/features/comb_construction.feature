Feature: Comb Construction

  Scenario: worker builds a hexagonal cell
    Given a worker bee assigned to comb duty
    When the bee secretes <amount> milligrams of wax
    Then a new hexagonal cell is added to the comb

  Scenario: queen lays egg in cell
    Given a fertilized queen bee
    And an empty cell in the brood comb
    When the queen lays a <kind> egg
    Then the cell contains a <kind> egg

  Scenario Outline: nursery temperature regulation
    Given the brood comb has <eggs> eggs
    And the ambient temperature is <ambient> degrees
    When <workers> bees cluster around the brood
    Then the brood temperature reaches <target> degrees

    Examples:
      | eggs | ambient | workers | target |
      | 500  | 28      | 20      | 35     |
      | 300  | 40      | 15      | 35     |
