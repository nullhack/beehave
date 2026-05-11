Feature: Decorator Test
  A simple feature to dogfood beehave's own workflow — tracking honey production in the hive.

  Rule: Hive honey tracking

    @id:a1b2c3d4
    Example: Adding nectar to the honey store
      Given a hive with <initial> grams of honey
      When a forager bee brings back <amount> grams of nectar
      Then the hive should contain <total> grams of honey

    @id:e5f6a7b8
    Example: Consuming honey during winter
      Given a hive with <initial> grams of honey
      When the colony consumes <amount> grams over winter
      Then the hive should contain <remaining> grams of honey

    @id:c9d0e1f2
    Example: Splitting honey between two hives
      Given a hive with <initial> grams of honey
      When the beekeeper splits it into <parts> equal jars
      Then each jar should contain <per_jar> grams of honey
