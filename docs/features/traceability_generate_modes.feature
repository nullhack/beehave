Feature: Traceability — Generate Modes

  beehave generate supports multiple output modes (human-readable and JSON), scope selection (all features or a single feature by name), and handles edge cases like empty features and malformed .feature files gracefully.

  Rules (Business):
  - beehave generate supports multiple output modes and handles edge cases
  - beehave generate is safe and idempotent — it prompts before appending, skips existing functions, and never modifies developer-owned content

  Constraints:
  - All commands support --json for programmatic consumption; human-readable by default
  - --json implies non-interactive mode: existing files are appended without prompting
  - Non-TTY mode auto-appends without prompting; output remains human-readable text format

  ## Changes

  | Session | Change |
  |---------|--------|
  | 2026-05-10 | Created: split from traceability_generate (output modes and edge cases) |

  Rule: beehave generate supports multiple output modes and handles edge cases
    As a developer
    I want beehave generate to work in CI/CD pipelines and handle errors gracefully
    So that I can integrate it into my development workflow

    @id:f2d4a6b8
    Example: Generate processes all features by default, single feature by name
      Given a project with multiple .feature files in docs/features/
      When the developer runs beehave generate
      Then all .feature files are processed and orphan scenarios receive test stubs

      Given a project with multiple .feature files in docs/features/
      When the developer runs beehave generate balance_accounting
      Then only balance_accounting.feature is processed

    @id:2f8a6d4b
    Example: Generate produces machine-readable JSON output
      Given a .feature file with orphan scenarios
      When the developer runs beehave generate --json
      Then the output is a JSON array of result objects
      And each object contains the file path, @id, scenario title, and action (created/appended/skipped)
      And --json implies non-interactive mode: existing files are appended without prompting

    @id:b3d5e7f9
    Example: --json auto-appends to existing files without prompt
      Given a test file that already exists with one test function
      When the developer runs beehave generate --json
      Then the new function is appended without prompting
      And the JSON output includes an entry with action "appended"

    @id:e1a3c5d7
    Example: Non-TTY mode auto-appends without prompting
      Given a test file that already exists and stdout is not a TTY
      When the developer runs beehave generate
      Then the new function is appended without prompting
      And the output is human-readable text format

    @id:a5c7e9f1
    Example: Generate handles features with no scenarios gracefully
      Given a .feature file that has no scenarios
      When the developer runs beehave generate
      Then no test file is created
      And the output reports "no scenarios found" for that feature

    @id:f7e9d1b3
    Example: Generate skips malformed .feature files and reports errors
      Given a malformed .feature file with an invalid syntax at line 12
      When the developer runs beehave generate
      Then a parse error is reported with the file path and line number
      And the malformed file is skipped
      And other .feature files continue to be processed
