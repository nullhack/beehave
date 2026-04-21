Feature: Cache management — incremental sync cache

  Beehave maintains a `.beehave_cache/features.json` file that stores content
  hashes of `.feature` files and generated stubs. On subsequent `sync` invocations,
  the cache allows beehave to skip unchanged files, making the tool fast enough
  for frequent developer use.

  The cache is not user-visible in normal operation: it auto-rebuilds silently if
  stale, missing, or corrupted. `beehave nest` adds `.beehave_cache/` to
  `.gitignore` automatically so the cache is never accidentally committed.

  Status: BASELINED (2026-04-21)

  Rules (Business):
  - Cache is advisory only: beehave must still produce correct results if the
    cache is deleted or tampered with.
  - Cache rebuilds must be silent and transparent.

  Constraints:
  - Cache corruption must not crash beehave; it must be treated as missing.

  Rule: Skip unchanged files using cache
    As a developer running sync frequently
    I want beehave to skip files that haven't changed since the last run
    So that sync completes in under one second for large projects

    @id:a1b2c3d4
    Example: Second run with no changes
      Given a project that was already synced in the previous run
      When beehave sync runs again
      Then no test files are created or modified and the process completes
        without scanning the full contents of unchanged `.feature` files

    @id:b2c3d4e5
    Example: Partial update after one file changes
      Given a project with ten `.feature` files where only one changed
      When beehave sync runs
      Then the changed file is fully processed and the other nine are skipped
        based on cache hits

  Rule: Recover silently from cache problems
    As a developer who may delete or corrupt the cache
    I want beehave to carry on as if the cache didn't exist
    So that I never have to repair it manually

    @id:c3d4e5f6
    Example: Missing cache rebuilt silently
      Given a project with no `.beehave_cache/` directory
      When beehave sync runs
      Then the cache directory and file are created silently and the full
        sync proceeds correctly

    @id:d4e5f6a7
    Example: Corrupted cache rebuilt silently
      Given a project where `.beehave_cache/features.json` contains invalid JSON
      When beehave sync runs
      Then the cache is discarded and rebuilt without error
