Feature: Cache Management — incremental sync cache
Status: BASELINED (2026-04-23)

Beehave maintains a JSON cache at `.beehave_cache/features.json` that stores
the last-known state of feature files and their stubs, enabling incremental
sync instead of full re-generation.

Rule: Cache location and format

  @id:8b1095aa
  Example: Cache file location
    Given a nested project
    When beehave sync runs
    Then a cache file is created at `.beehave_cache/features.json`

  @id:1add948d
  Example: Cache is added to gitignore by nest
    Given a project being nested for the first time
    When the user runs "beehave nest"
    Then `.beehave_cache/` is added to `.gitignore`

Rule: Cache lifecycle

  @id:37170612
  Example: Missing cache is rebuilt silently
    Given a project with no cache file
    When beehave sync runs
    Then the cache is rebuilt from the current `.feature` files
    And no error or warning is produced

  @id:d7ecdb33
  Example: Corrupted cache is rebuilt silently
    Given a project with an invalid JSON cache file
    When beehave sync runs
    Then the cache is rebuilt from the current `.feature` files
    And no error or warning is produced

  @id:dafb15f1
  Example: Cache is not user-visible in normal operation
    Given a project with a valid cache
    When the user runs "beehave status"
    Then the cache is used internally but not displayed
