Feature: Colony Winter Preparation

  As Beatrice, the winter logistics coordinator in the Obsidian Hive
  I want to ensure honey stores are sufficient before the first frost
  So that the colony survives the winter without starvation

  Rule: Honey reserve verification

    @id:hatch006
    Example: Winter preparation passes when honey reserve exceeds minimum
      Given the honey reserve is at 85 percent capacity
      When the winter readiness check is performed
      Then the colony status is set to WINTER-READY

    @id:hatch007
    Example: Winter preparation fails when honey reserve is insufficient
      Given the honey reserve is below 60 percent capacity
      When the winter readiness check is performed
      Then the colony status is set to AT-RISK and an alert is raised for Beatrice
