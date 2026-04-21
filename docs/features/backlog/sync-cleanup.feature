Feature: Sync-Cleanup — handle orphaned test stubs when `.feature` files are deleted

  As a developer cleaning up obsolete scenarios,
  I want beehave to detect test stubs whose `@id` no longer exists in any
    `.feature` file and warn me about the orphan,
  so that my test suite does not accumulate dead code.

  An orphan is triggered when the `@id` embedded in a test function name has no
  matching `@id` in any `.feature` file across the project. Beehave warns only —
  it leaves the stub completely unchanged. The developer deletes orphans manually.

  When a `.feature` file is deleted, beehave warns only (C5 behavior). The
  corresponding test stubs become orphans and are surfaced by orphan detection.

  When a feature is renamed (slug changes but IDs still match), beehave renames
  the test function to match the new slug while preserving the body. This is
  sync-update territory, not cleanup.

  When a test stub is in the wrong location (IDs match but path is incorrect),
  beehave moves the test function/file to the correct location, preserving the body.

  Status: BASELINED (2026-04-21)

  Rules (Business):
  - Orphan detection is based purely on `@id` matching; any stub function whose
    `@id` cannot be found in any `.feature` file is an orphan.
  - Stubs are never deleted automatically; beehave only warns.

  Constraints:
  - Orphan warnings are part of the standard CLI output contract (silent unless
    `--verbose` or `--json` is used).

  Rule: Detect orphaned stubs when Example is removed
    As a developer deleting obsolete scenarios
    I want beehave to surface the resulting dead test functions
    So that I can clean them up manually

    @id:e7f8a9b0
    Example: Single orphan after Example deletion
      Given a test stub `test_login_a1b2c3d4` exists
        and no `.feature` Example with `@id:a1b2c3d4` exists anywhere
      When beehave sync runs
      Then a warning is emitted naming the orphan function and file

    @id:f8a9b0c1
    Example: No warning when @id still exists
      Given a test stub `test_login_a1b2c3d4` exists
        and a `.feature` Example with `@id:a1b2c3d4` also exists
      When beehave sync runs
      Then no orphan warning is emitted for that function

  Rule: Warn when entire feature file is deleted
    As a developer removing a feature entirely
    I want beehave to alert me that test stubs mapping to that feature exist
    So that I can decide whether to archive or delete them

    @id:a9b0c1d2
    Example: Feature file deletion triggers C5 warning
      Given a `.feature` file `docs/features/backlog/auth.feature` that was
        previously present is now absent
      When beehave sync runs
      Then a warning is emitted naming the deleted file

  Rule: Relocate stubs to correct directory after feature rename
    As a developer renaming or moving a `.feature` file
    I want the test files to follow the feature into the new directory
    So that the file tree stays organized

    @id:b0c1d2e3
    Example: Stub moves when feature slug changes
      Given a `.feature` file was renamed from `auth.feature` to
        `authentication.feature` but `@id`s still exist
      When beehave sync runs
      Then the test file `tests/features/auth/rules_test.py` is moved to
        `tests/features/authentication/rules_test.py` and its contents are
        unchanged except for function renames (sync-update)

    @id:c1d2e3f4
    Example: Stub moves when feature file moves between stages
      Given a `.feature` file moved from `docs/features/backlog/login.feature`
        to `docs/features/in-progress/login.feature`
      When beehave sync runs
      Then no file movement or rename happens in `tests/features/` because
        stage subfolder does not affect mapping
