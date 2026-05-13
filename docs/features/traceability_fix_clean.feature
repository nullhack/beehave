Feature: Traceability — Fix and Clean

  beehave fix corrects decorator text and adds missing step decorators to align test code with .feature files. beehave clean removes orphan test functions that no longer correspond to .feature scenarios. These commands escalate in risk: fix (moderate) → clean (destructive).

  Rules (Business):
  - CLI commands follow the principle "report first, explicit flags for actions"
  - Fix and clean escalate in risk: fix (moderate) → clean (destructive)
  - beehave owns @id tags and decorator text in test files
  - Developers own function bodies — beehave never modifies function bodies

  Constraints:
  - .feature files are the source of truth — beehave never modifies step text in .feature files
  - Fix and clean require explicit confirmation or flags before modifying files
  - Fix and clean produce idempotent results when run multiple times

  ## Changes

  | Session | Change |
  |---------|--------|
  | 2026-05-10 | Created: split from traceability_generate_fix_clean (Rules: fix + clean) |

  Rule: beehave fix corrects decorator text and adds missing steps
    As a developer
    I want beehave fix to align my test decorators with .feature step text
    So that vocabulary drift is corrected automatically

    @id:b8e2f6d7
    Example: Fix corrects decorator text to match .feature
      Given a test with @Given("a user with an balance <initial>")
      And a .feature step "Given a user with balance <initial>"
      When the developer runs beehave fix
      Then the decorator is corrected to @Given("a user with balance <initial>")

    @id:4a9c3e5f
    Example: Fix adds missing step decorators
      Given a .feature scenario with 3 steps but a test with only 2 decorators
      When the developer runs beehave fix
      Then the missing decorator is added with correct step text and keyword
      And the corresponding <placeholder> names are added to the function parameters

    @id:d2c7a8b1
    Example: Fix supports dry-run mode
      When the developer runs beehave fix --dry-run
      Then a diff of proposed changes is shown without modifying any files

  Rule: beehave clean removes orphan test functions
    As a developer
    I want beehave clean to remove test functions that no longer correspond to .feature scenarios
    So that my test suite stays clean after refactoring

    @id:6f1e9d4c
    Example: Clean requires interactive confirmation
      Given 3 orphan test functions with no matching .feature scenarios
      When the developer runs beehave clean
      Then the developer is prompted "Remove 3 orphan tests? [y/N]"
      And if yes, the functions are deleted from their files

    @id:a3b8c5d2
    Example: Clean skips confirmation with --force
      When the developer runs beehave clean --force
      Then orphan test functions are deleted without confirmation prompt