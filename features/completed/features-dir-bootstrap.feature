Feature: Features directory bootstrap

  Status: BASELINED (2026-04-18)

  Rules (Business):
  - Bootstrap runs as the first action of every pytest invocation, before stub sync
  - Bootstrap only runs if the root features directory exists; if it does not exist, it is skipped
  - All three subfolders (backlog/, in-progress/, completed/) must exist; each missing one is created independently
  - Only .feature files directly in the root features directory (not inside any subfolder) are migrated to backlog/
  - Non-.feature files in the root features directory (e.g. discovery.md) are never moved
  - Files already inside backlog/, in-progress/, or completed/ are never touched by migration
  - Name collision during migration: leave the root-level file in place and emit a warning; do not overwrite
  - If the structure is already correct and no root-level .feature files exist, the bootstrap is a silent no-op

  Constraints:
  - Bootstrap must complete before stub sync begins so that migrated files are available for stub sync in the same run
  - Terminal output style must be consistent with the existing stub sync reporting

  Rule: Subfolder creation
    As a developer
    I want the plugin to create missing canonical subfolders automatically
    So that the features directory structure is always ready for stub sync without manual setup

    @id:3a1f8c2e
    Example: All three subfolders are created when none exist
      Given the features directory exists with no backlog, in-progress, or completed subfolders
      When pytest is invoked
      Then the backlog, in-progress, and completed subfolders all exist inside the features directory

    @id:b7d4e091
    Example: Only the missing subfolders are created when some already exist
      Given the features directory exists with a backlog subfolder but no in-progress or completed subfolders
      When pytest is invoked
      Then the in-progress and completed subfolders are created and the backlog subfolder is unchanged

    @id:c2a53f7d
    Example: Subfolder creation is reported to the terminal
      Given the features directory exists with no backlog, in-progress, or completed subfolders
      When pytest is invoked
      Then the terminal output names each subfolder that was created

  Rule: Feature file migration
    As a developer
    I want .feature files in the root features directory to be moved to backlog automatically
    So that existing feature files are immediately available for stub sync without manual reorganisation

    @id:e8b61d04
    Example: A .feature file in the root features directory is moved to backlog
      Given the features directory contains a .feature file directly (not inside any subfolder)
      When pytest is invoked
      Then that .feature file exists in the backlog subfolder and no longer exists in the root features directory

    @id:f3c97a52
    Example: Non-.feature files in the root features directory are not moved
      Given the features directory contains a non-.feature file (e.g. discovery.md) directly in the root
      When pytest is invoked
      Then that file remains in the root features directory and is not moved to backlog

    @id:a9d02b6e
    Example: Files already inside a subfolder are not moved
      Given the features directory contains a .feature file inside the in-progress subfolder
      When pytest is invoked
      Then that file remains in the in-progress subfolder and is not moved to backlog

    @id:d1e74c83
    Example: Migration is reported to the terminal
      Given the features directory contains a .feature file directly in the root
      When pytest is invoked
      Then the terminal output names the file that was moved to backlog

  Rule: Migration collision handling
    As a developer
    I want to be warned when a root-level .feature file cannot be migrated due to a name conflict
    So that I can resolve the conflict manually without losing either file

    @id:7f2a0d51
    Example: Root-level .feature file is left in place when a same-named file exists in backlog
      Given the features directory contains root-level feature.feature and backlog/feature.feature already exists
      When pytest is invoked
      Then root-level feature.feature is not moved and backlog/feature.feature is unchanged

    @id:8c3b1e96
    Example: A collision warning is emitted to the terminal
      Given the features directory contains root-level feature.feature and backlog/feature.feature already exists
      When pytest is invoked
      Then the terminal output contains a warning naming the conflicting file and its location

  Rule: No-op when structure is correct
    As a developer
    I want the bootstrap to produce no output when the features directory is already well-structured
    So that normal pytest runs are not cluttered with unnecessary messages

    @id:5e6f9b17
    Example: Bootstrap produces no terminal output when structure is already correct
      Given the features directory contains backlog, in-progress, and completed subfolders and no root-level .feature files
      When pytest is invoked
      Then the terminal output contains no bootstrap messages

    @id:2d8a4c70
    Example: Bootstrap is skipped when the features directory does not exist
      Given the features directory does not exist
      When pytest is invoked
      Then pytest completes collection without errors and no bootstrap messages appear in the terminal
