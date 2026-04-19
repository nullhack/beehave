Feature: Royal Jelly Production

  As Beatrice, a worker bee in the Obsidian Hive
  I want to complete my assigned foraging route
  So that the colony has enough nectar for the season

  Rule: Forager readiness

    @id:hatch001
    Example: Forager departs when pollen reserve is below threshold
      Given the pollen reserve is below 30 percent
      When the forager sensor detects the shortage
      Then Beatrice departs for the meadow within one waggle cycle

    Example: Untagged scenario triggers auto-ID assignment
      Given the hive registers a new forager
      When the forager completes orientation
      Then the forager is assigned a unique scout ID

    @deprecated
    Example: Legacy hive-entry handshake (deprecated)
      Given an older forager approaches the hive entrance
      When the guard bee checks the legacy handshake
      Then the handshake is accepted but logged as deprecated

  Rule: Nectar quality control

    @id:hatch002
    Example: Low-quality nectar is rejected at the gate
      Given a forager returns with nectar of quality below 0.4 brix
      When the gate inspector evaluates the sample
      Then the nectar is rejected and the forager is sent to a higher-quality source
