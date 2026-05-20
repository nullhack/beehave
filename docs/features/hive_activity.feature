Feature: Hive Activity

  Background:
    Given the hive is active

  Scenario Outline: honey production from nectar
    Given the hive has <nectar> grams of nectar
    And the evaporation rate is <rate> percent
    When the bees fan their wings for <hours> hours
    Then the hive produces <honey> grams of honey

    Examples:
      | nectar | rate | hours | honey |
      | 100    | 20   | 8     | 80    |
      | 200    | 25   | 12    | 150   |
      | 50     | 30   | 6     | 35    |

  Rule: Hive defense

    Background:
      Given the entrance has 2 guards

    Scenario: guard bee inspects visitor
      Given a visitor bee with <scent> colony odor
      When the guard inspects the visitor for "floral" scent
      Then the visitor is <outcome>

  Rule: Hive Foraging

    Scenario: forager returns with nectar
      Given a forager bee named <name>
      When the forager returns with <volume> milliliters of nectar
      Then the hive stores <volume> milliliters of nectar
