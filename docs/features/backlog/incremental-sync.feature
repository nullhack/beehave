Feature: Incremental sync via mtime+size cache
  On every pytest run, the sync engine currently performs 2–3 full reads of every .feature file
  and every *_test.py stub — unconditionally, even when nothing has changed. For a developer in
  watch mode (fast TDD loop), this is felt as constant unnecessary I/O on every save.

  A lightweight JSON cache file (.beehave-cache/sync_state.json, gitignored) stores per-file
  {mtime, size} entries. On each pytest_configure, the plugin stat()-checks each file against
  the cache: unchanged files are skipped entirely; changed or new files are fully re-processed.
  After sync, the cache is updated with the new stats for any file that was touched. In CI
  (read-only mode) and when --beehave-no-cache is passed, the cache is bypassed entirely and
  a full run is performed.

  Status: BASELINED (2026-04-20)

  Rules (Business):
  - A file whose mtime AND size both match the cache entry is considered unchanged and skipped
  - A file whose mtime OR size differs from the cache entry is considered stale and fully re-processed
  - After any file is written (new @id tag, updated docstring, etc.), its new stat is stored in the cache
  - When no cache file exists, a full run is performed and the cache is written on completion
  - When the cache file is malformed (invalid JSON), it is treated as absent — full run, cache rewritten
  - In CI (read-only filesystem), the cache is not read and not written; a full run is always performed
  - --beehave-no-cache forces a full run and suppresses all cache reads and writes
  - cache_path under [tool.beehave] overrides the default .beehave-cache/ directory

  Constraints:
  - Cache file is .beehave-cache/sync_state.json relative to the project root (configurable)
  - Cache directory and file are created automatically on first write
  - Cache is gitignored — the plugin must not add it to version control
  - stat() is the only I/O performed on unchanged files — no open(), no read()
  - Cache entries use string keys (absolute or project-relative path) and {mtime, size} values
  - A failed write must not corrupt the existing cache — write to a temp file and rename atomically

  Rule: Cache hit skips processing
    As a developer in watch mode
    I want unchanged files to be skipped entirely on each pytest run
    So that repeated runs with no file changes complete with minimal I/O

    @id:3a7f2c1e
    Example: Unchanged feature file is not re-processed on second run
      Given a project whose .feature files have not changed since the last pytest run
      And a valid cache file exists with matching mtime and size for each .feature file
      When pytest is invoked
      Then no .feature file is opened or read during sync

    @id:b4d8e5f9
    Example: Unchanged stub file is not re-processed on second run
      Given a project whose *_test.py stub files have not changed since the last pytest run
      And a valid cache file exists with matching mtime and size for each stub file
      When pytest is invoked
      Then no stub file is opened or read during sync

    @id:c2a1f6b3
    Example: Cache hit is per-file — one changed file does not invalidate others
      Given a project with three .feature files where only one has changed since the last run
      And a valid cache file exists with matching entries for the two unchanged files
      When pytest is invoked
      Then only the changed .feature file is re-processed
      And the two unchanged .feature files are not opened or read

  Rule: Cache miss triggers full re-processing
    As a developer
    I want any changed file to be fully re-processed
    So that my test stubs always reflect the current state of my acceptance criteria

    @id:d9e3b7a4
    Example: Feature file with changed mtime is fully re-processed
      Given a valid cache file exists for a .feature file
      And the .feature file's mtime has changed since the cache was written
      When pytest is invoked
      Then the .feature file is fully re-processed by the sync engine

    @id:e5c8f2d1
    Example: Feature file with changed size is fully re-processed
      Given a valid cache file exists for a .feature file
      And the .feature file's size has changed since the cache was written
      When pytest is invoked
      Then the .feature file is fully re-processed by the sync engine

    @id:f1b6a3c9
    Example: Feature file absent from cache is fully re-processed
      Given a valid cache file exists but does not contain an entry for a particular .feature file
      When pytest is invoked
      Then that .feature file is fully re-processed by the sync engine

  Rule: Cache updated after write
    As a developer
    I want the cache to reflect the new state of any file the plugin writes
    So that the next run correctly skips files that were just updated

    @id:a8d4e7f2
    Example: Cache entry is updated after @id tag is written to a feature file
      Given a .feature file that required a new @id tag to be written
      When pytest completes the sync
      Then the cache entry for that .feature file contains the mtime and size of the written file

    @id:b3c9f1e6
    Example: Cache entry is updated after a stub file is written
      Given a stub file that was created or updated during sync
      When pytest completes the sync
      Then the cache entry for that stub file contains the mtime and size of the written file

    @id:c7a2d5b8
    Example: Cache is not updated for a file whose write failed
      Given a .feature file that required a write but the write operation failed
      When pytest completes the sync
      Then the cache entry for that .feature file is not updated

  Rule: Cold start performs full run and writes cache
    As a developer setting up a new project
    I want the cache to be created automatically on first use
    So that subsequent runs benefit from incremental sync without any manual setup

    @id:d1f8c4a3
    Example: No cache file triggers a full run
      Given no .beehave-cache/sync_state.json file exists
      When pytest is invoked
      Then all .feature files and stub files are fully processed

    @id:e6b3a9f7
    Example: Cache file is written after a successful cold-start run
      Given no .beehave-cache/sync_state.json file exists
      When pytest completes the sync
      Then .beehave-cache/sync_state.json exists and contains entries for all processed files

    @id:f4c1e2d8
    Example: Malformed cache file is treated as absent
      Given .beehave-cache/sync_state.json exists but contains invalid JSON
      When pytest is invoked
      Then all .feature files and stub files are fully processed
      And the cache file is overwritten with valid JSON after sync completes

    @id:a5d7b6c2
    Example: Cache directory is created automatically when it does not exist
      Given the .beehave-cache/ directory does not exist
      When pytest completes the sync
      Then the .beehave-cache/ directory exists and contains sync_state.json

  Rule: CI mode bypasses cache entirely
    As a CI pipeline
    I want the cache to be ignored so that every CI run is a full, reproducible sync
    So that CI results are never affected by a stale or missing cache file

    @id:b8e4f3a1
    Example: Cache is not read in CI mode
      Given the plugin detects a read-only filesystem (CI environment)
      When pytest is invoked
      Then the cache file is not read and all files are fully processed

    @id:c3f9d2b6
    Example: Cache is not written in CI mode
      Given the plugin detects a read-only filesystem (CI environment)
      When pytest completes the sync
      Then the cache file is not created or modified

  Rule: --beehave-no-cache flag forces full run
    As a developer
    I want to be able to force a full sync run on demand
    So that I can diagnose issues or reset the cache without deleting files manually

    @id:d7a5c8e4
    Example: --beehave-no-cache forces all files to be re-processed
      Given a valid cache file exists with up-to-date entries for all files
      When pytest is invoked with --beehave-no-cache
      Then all .feature files and stub files are fully processed regardless of cache state

    @id:e2b1f6d9
    Example: --beehave-no-cache suppresses cache write
      Given a valid cache file exists
      When pytest is invoked with --beehave-no-cache
      Then the cache file is not modified after sync completes

  Rule: Configurable cache path
    As a developer
    I want to configure the cache directory location via pyproject.toml
    So that I can place the cache outside the project root if needed (e.g. in a temp directory)

    @id:f9c3a7d5
    Example: Custom cache_path is used when configured
      Given pyproject.toml contains [tool.beehave] cache_path = ".tmp/beehave-cache"
      When pytest completes the sync
      Then the cache file is written to .tmp/beehave-cache/sync_state.json
      And no file is written to the default .beehave-cache/ directory

    @id:a4e8b2f1
    Example: Default cache path is used when cache_path is not configured
      Given pyproject.toml contains no cache_path key under [tool.beehave]
      When pytest completes the sync
      Then the cache file is written to .beehave-cache/sync_state.json relative to the project root
