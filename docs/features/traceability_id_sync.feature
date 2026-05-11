Feature: Traceability — @id Tags and Sync

  beehave links test functions to .feature scenarios via @id tags, providing traceability and the beehave sync command to assign IDs and report orphans. The .feature file is the source of truth; test files are derived artifacts that beehave can create to match.

  Rules (Business):
  - @id tags use the format @id:<8-char-random-id> and are owned by beehave
  - IDs are generated once and are permanent — editing scenario text does not change the ID
  - Test function names include the @id as a suffix: test_*_<id>
  - beehave sync is safe and idempotent — running it twice produces the same result

  Constraints:
  - pytest collection is read-only — never modifies .feature files or test files
  - .feature files are the source of truth — beehave never modifies step text in .feature files
  - Developers own function bodies — beehave never modifies function bodies
  - beehave owns @id tags in .feature files and test files

  ## Changes

  | Session | Change |
  |---------|--------|
  | 2026-05-10 | Created: split from traceability_cli_commands (Rules 1–2) |
  | 2026-05-10 | Spec review: moved @id:3e9b1c6a to 2b feature (beehave generate out of scope); split @id:c7f2a8d5 into two Examples (single-observable-outcome); added @id:a1f4e8b7 (ID permanence); removed out-of-scope rules (step text matching, CLI principle) |

  Rule: @id tags link .feature scenarios to test functions
    As a QA engineer
    I want every .feature scenario to have a unique @id tag that links to a test function
    So that I can verify that every scenario has a corresponding test

    @id:c7f2a8d5
    Example: @id tag format in .feature file
      Given a .feature scenario without an @id tag
      When the developer runs beehave sync
      Then beehave generates an 8-character random ID and writes @id:<id> into the .feature file

    @id:a1f4e8b7
    Example: @id tags are permanent across edits
      Given a .feature scenario with @id:c7f2a8d5
      When the developer edits the scenario text
      Then the @id tag remains unchanged

    @id:6d4f8a2e
    Example: Orphan scenario detection
      Given a .feature scenario with @id:m3n4o5p6 that has no matching test function
      When the developer runs beehave sync
      Then the scenario is reported as an orphan scenario

    @id:f1c7d5b9
    Example: Orphan test detection
      Given a test function with @id suffix that has no matching .feature scenario
      When the developer runs beehave sync
      Then the test is reported as an orphan test

  Rule: beehave sync assigns @id tags and reports orphans
    As a developer
    I want beehave sync to automatically assign @id tags to .feature scenarios and report orphans
    So that traceability is maintained without manual ID management

    @id:2b8e4a7d
    Example: Sync assigns IDs to scenarios without them
      Given a .feature file with three scenarios, none having @id tags
      When the developer runs beehave sync
      Then each scenario gets a unique random 8-character @id tag
      And the .feature file is updated with the new tags

    @id:9c3f6e1a
    Example: Sync replaces malformed or manual @id tags
      Given a .feature scenario with @id:my_custom_name
      When the developer runs beehave sync
      Then beehave replaces @id:my_custom_name with a beehave-generated 8-char random ID

    @id:5a7d2b8f
    Example: Sync is idempotent
      Given a .feature file where all scenarios already have beehave-generated @id tags
      When the developer runs beehave sync
      Then no changes are made to the .feature file