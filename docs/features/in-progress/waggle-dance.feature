# language: en
Feature: Waggle Dance Communication

  Background:
    Given the hive is in active foraging mode
    And the dance floor is clear of obstacles

  Rule: Direction encoding

    @id:hatch003
    Example: Scout encodes flower direction in waggle run angle
      Given a scout has located flowers 200 metres to the north-east
      When the scout performs the waggle dance
      Then the waggle run angle matches the sun-relative bearing to the flowers

  Rule: Distance encoding

    @id:hatch004
    Scenario Outline: Scout encodes distance via waggle run duration
      Given a scout has located flowers at <distance> metres
      When the scout performs the waggle dance
      Then the waggle run lasts approximately <duration> milliseconds

      Examples:
        | distance | duration |
        | 100      | 250      |
        | 500      | 875      |
        | 1000     | 1500     |

    @id:hatch005
    Example: Scout provides a data table of visited flower patches
      Given the scout returns from a multi-patch forage
      When the scout performs the waggle dance
      Then the flower patch register contains the following entries:
        | patch_id | species       | quality |
        | P-001    | Lavender      | 0.92    |
        | P-002    | Clover        | 0.85    |
        | P-003    | Sunflower     | 0.78    |
