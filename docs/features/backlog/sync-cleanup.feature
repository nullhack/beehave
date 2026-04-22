Feature: sync-cleanup — handle orphaned and misplaced stubs

  Detects and reports on test stubs whose @id no longer matches any Example in any .feature file
  (orphans), and corrects stubs that are in the wrong directory by moving them to the right
  location. When a .feature file is deleted, beehave warns and the resulting orphan stubs are
  flagged by orphan detection. beehave never deletes stubs automatically.

  Status: BASELINED (2026-04-22)

  Rules (Business):
  - Orphaned stubs are warned about and never deleted automatically
  - A stub in the wrong directory is moved to the correct location, body preserved
  - A deleted .feature file triggers a warning

  Constraints:
  - Orphan: a test function whose name contains an @id absent from all .feature files
  - Path correction applies when @id matches but directory path does not

  Rule: Orphan detection
    As a developer
    I want beehave to tell me when a stub has no matching Example
    So that I can decide what to do with it rather than having it silently removed

    @id:2d9fa007
    Example: Stub with no matching @id in any .feature file is reported as orphan
      Given a test function test_honey_flow_a1b2c3d4 where @id:a1b2c3d4 does not exist in any .feature file
      When beehave sync runs
      Then beehave emits a warning identifying the orphan stub by name and file path

    @id:bc9ca466
    Example: Orphan stub is never deleted automatically
      Given a test function whose @id has no matching Example
      When beehave sync runs
      Then the test function file is unchanged after sync

    @id:eed4cdbb
    Example: Stub with a matching @id in a .feature file is not flagged as orphan
      Given a test function test_honey_flow_a1b2c3d4 and @id:a1b2c3d4 exists in a .feature file
      When beehave sync runs
      Then no orphan warning is emitted for that stub

  Rule: Path correction
    As a developer
    I want beehave to move misplaced stubs to the correct location
    So that my test layout stays consistent with my .feature file structure

    @id:0e077f6e
    Example: Stub in wrong directory is moved to the correct path
      Given a test function whose @id matches an Example but the file is in the wrong feature slug directory
      When beehave sync runs
      Then the stub function is moved to tests/features/<correct_slug>/<rule_slug>_test.py with its body intact

    @id:fb241843
    Example: Moved stub body is byte-for-byte unchanged
      Given a misplaced stub with an implemented body
      When beehave sync moves it to the correct path
      Then the function body in the new location is identical to the original

  Rule: Deleted feature file warning
    As a developer
    I want beehave to warn me when a .feature file I had stubs for has been deleted
    So that I know orphan stubs exist that need manual review

    @id:20d52a9d
    Example: Deleting a .feature file causes a warning on next sync
      Given a .feature file that had stubs generated for it is deleted
      When beehave sync runs
      Then beehave emits a warning identifying the deleted feature and its orphaned stubs
