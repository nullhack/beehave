Feature: cache-management — incremental sync cache

  Maintains a JSON cache at .beehave_cache/features.json to track the last-known state of every
  .feature file. On each sync, only changed files are fully reprocessed, keeping sync fast on
  large projects. The cache is invisible in normal operation and never committed to version control.

  Status: BASELINED (2026-04-22)

  Rules (Business):
  - Cache is auto-created on first sync and updated incrementally on every subsequent sync
  - A missing, stale, or corrupted cache is rebuilt silently without surfacing an error to the user

  Constraints:
  - Cache file is added to .gitignore by beehave nest
  - Cache is not a user-visible artifact

  Rule: Cache creation and update
    As a developer
    I want beehave to maintain a cache automatically
    So that repeated syncs on large projects are fast without any manual cache management

    @id:b0d4d606
    Example: Cache file is created on first sync
      Given no .beehave_cache/features.json exists
      When beehave sync runs for the first time
      Then .beehave_cache/features.json is created

    @id:abeb4807
    Example: Cache is updated after each sync
      Given .beehave_cache/features.json exists from a previous sync
      When beehave sync runs again after a .feature file changes
      Then .beehave_cache/features.json reflects the new state of the changed file

    @id:45ac0e98
    Example: Unchanged files are not reprocessed
      Given .beehave_cache/features.json is up to date for all .feature files
      When beehave sync runs
      Then only files whose content has changed since the last sync are fully reprocessed

  Rule: Cache resilience
    As a developer
    I want beehave to recover silently from a missing or corrupted cache
    So that deleting or corrupting the cache never breaks my workflow

    @id:29259d33
    Example: Missing cache triggers a silent full rebuild
      Given .beehave_cache/features.json has been deleted
      When beehave sync runs
      Then beehave rebuilds the cache from scratch with no error or warning to the user

    @id:40c67579
    Example: Corrupted cache triggers a silent full rebuild
      Given .beehave_cache/features.json contains invalid JSON
      When beehave sync runs
      Then beehave rebuilds the cache from scratch with no error or warning to the user

  Rule: Cache invisibility
    As a developer
    I want the cache to be invisible in normal operation
    So that it does not pollute my repository or require any maintenance

    @id:79aa550e
    Example: Cache directory is added to .gitignore by nest
      Given beehave nest is run on a clean project
      When the project's .gitignore is inspected
      Then .beehave_cache/ appears in .gitignore

    @id:881b03fe
    Example: No cache-related output appears in default sync output
      Given a valid cache exists
      When beehave sync runs with no output flags
      Then no cache-related messages appear in stdout or stderr
