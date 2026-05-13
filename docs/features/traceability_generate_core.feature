Feature: Traceability — Generate Core

  beehave generate creates test stub files with correct decorators and strategy variables for .feature scenarios that lack matching test functions. The .feature file is the source of truth; test files are derived artifacts that beehave creates to match. Generate is safe (additive only) and idempotent.

  Rules (Business):
  - beehave generate creates importable, convention-compliant test stubs for every orphan scenario
  - beehave generate is safe and idempotent — it prompts before appending, skips existing functions, and never modifies developer-owned content

  Constraints:
  - .feature files are the source of truth — beehave never modifies step text in .feature files
  - beehave owns decorator text and @id tags in test files; developers own function bodies (generate only writes decorator text, signatures, and stub bodies, never existing function bodies)
  - Generate creates new files (writes) or adds functions to existing files (appends). Both operations are additive-only. Appending triggers an interactive prompt in TTY mode; in non-TTY or --json mode, append proceeds automatically.
  - Generate is idempotent — it skips scenarios that already have matching test functions

  ## Changes

  | Session | Change |
  |---------|--------|
  | 2026-05-10 | Created: split from traceability_generate (core generation logic) |

  Rule: beehave generate creates test stubs for orphan scenarios
    As a developer
    I want beehave generate to create test stub files with correct decorators and strategy variables
    So that I can start implementing tests quickly

    @id:3e9b1c6a
    Example: Test function name includes @id suffix
      Given a .feature scenario with @id:kx7m2p9q
      When beehave generate creates a test function for this scenario
      Then the generated test function is named test_<scenario_title_snake_case>_kx7m2p9q
      And the snake_case portion is NFKD-normalized, truncated to 80 characters, and the @id suffix is always included in full

    @id:e4c1b9d3
    Example: Generate creates a new test file for a feature with no existing tests
      Given a .feature file "balance_accounting.feature" with scenarios but no matching test directory
      When the developer runs beehave generate
      Then tests/features/balance_accounting/default_test.py is created
      And it contains imports, strategy variables, step decorators, @Example decorators, and a function with ... body
      And the directory tests/features/balance_accounting/ is created if it does not exist

    @id:7f6a3e8c
    Example: Generate appends to an existing file
      Given a test file that already exists with one test function
      When beehave generate tries to add another function to the same file
      Then the developer is prompted "file already exists. Add function? [y/N]"
      And if yes, the function is appended to the end of the file

    @id:1d9b5c4a
    Example: Generate is idempotent
      Given a test file that already has a function for @id:kx7m2p9q
      When beehave generate encounters the same @id
      Then it skips with a warning "function for @id:kx7m2p9q already exists"

    @id:c8e2f4a6
    Example: Generate skips matched scenarios and creates stubs for orphans
      Given a .feature file with three scenarios where two have matching test functions and one is an orphan
      When the developer runs beehave generate
      Then the orphan scenario gets a test stub created
      And the two matched scenarios are skipped with a warning

    @id:d6f8a2c4
    Example: Snake_case conversion handles special characters
      Given a .feature scenario titled "Ünïcödé: a café's 3 attempts"
      When beehave generate creates a test function
      Then the function name starts with "unicode_a_cafe_s_scenario_3_attempts_" followed by the @id
