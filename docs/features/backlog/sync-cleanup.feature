Feature: Sync Cleanup — handle orphaned test stubs
Status: BASELINED (2026-04-23)

`beehave sync` detects orphaned test stubs — functions whose `@id` has no
matching Example in any `.feature` file — and warns without deleting them.
It also handles stubs in the wrong location.

Rule: Orphan detection triggers a warning

  @id:5390072a
  Example: Orphaned stub is detected
    Given a test function `test_login_a1b2c3d4` with no matching `@id:a1b2c3d4` in any `.feature` file
    When beehave sync runs
    Then a warning is issued about the orphaned stub
    And the stub is left completely unchanged

  @id:1a40571d
  Example: Deleted feature file creates orphans
    Given a `.feature` file is deleted
    And stubs exist for Examples from that file
    When beehave sync runs
    Then the stubs are identified as orphans and warnings are issued

Rule: Feature rename with matching IDs triggers function rename

  @id:ffe09e14
  Example: Slug change with same ID renames the function
    Given a stub `test_login_a1b2c3d4` and `@id:a1b2c3d4` exists in a renamed feature file
    When beehave sync runs
    Then the function is renamed to match the new slug
    And the test body is preserved

Rule: Stub in wrong location is moved

  @id:dc668d29
  Example: Test function in wrong directory is relocated
    Given a test function `test_login_a1b2c3d4` in `tests/features/old_name/`
    And `@id:a1b2c3d4` maps to feature "new_name"
    When beehave sync runs
    Then the function is moved to `tests/features/new_name/`
    And the test body is preserved
