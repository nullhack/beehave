Feature: Feature File Parsing and Validation

  beehave parses .feature files and validates test structure against them at collection time. Validation includes exact step text matching, step ordering, placeholder-parameter matching, and @id traceability. The .feature file is the source of truth for vocabulary and structure.

  Rules (Business):
  - Step text matching is exact — character-for-character after stripping Gherkin keywords and tokenizing <placeholder> variables
  - Step ordering must follow Given → When → Then; @And/@But inherit from the preceding step type
  - Every <placeholder> name in step text must appear as a function parameter
  - .feature files are located in docs/features/ by default (configurable in pyproject.toml)
  - One .feature file per feature, one test directory per feature (1:1 mapping)
  - Tests without .feature files operate at adoption level 1 with limited validation

  Constraints:
  - Validation is collection-time (CLI commands) — zero runtime overhead on passing tests
  - Future pytest plugin will provide real-time validation during test collection
  - Feature file location is configurable in pyproject.toml under [tool.beehave]

  ## Changes

  | Session | Change |
  |---------|--------|
  | 2026-05-10 | Created: initial feature specification |
  | 2026-05-10 | Replaced descriptive @id names with 8-char hex IDs per collection_mechanics spec |

  Rule: .feature files map to test modules via Rule structure
    As a developer
    I want .feature files to map predictably to test module files
    So that I can find the corresponding test for any scenario

    @id:2a8f5c1e
    Example: Feature with no Rule maps to default_test.py
      Given a .feature file "balance_accounting.feature" with no Rule defined
      When beehave resolves the test module path
      Then it maps to tests/features/balance_accounting/default_test.py

    @id:7d3b9e6a
    Example: Feature with Rules maps to <rule_name>_test.py
      Given a .feature file "balance_accounting.feature" with Rule "Total calculation"
      When beehave resolves the test module path
      Then it maps to tests/features/balance_accounting/total_calculation_test.py

  Rule: Step text must match exactly between .feature and decorators
    As a team lead
    I want beehave to enforce vocabulary consistency between .feature files and test code
    So that vocabulary drift is caught automatically

    @id:4c1f8d3b
    Example: Exact step text match passes validation
      Given a .feature step "Given a user with balance <initial>"
      And a test decorator @Given("a user with balance <initial>")
      When beehave validates the step
      Then no mismatch is reported

    @id:e6a2c7f9
    Example: Step text mismatch fails validation
      Given a .feature step "Given a user with balance <initial>"
      And a test decorator @Given("a user with an balance <initial>")
      When beehave validates the step
      Then a mismatch is reported with the exact difference

  Rule: Step ordering validation ensures Given before When before Then
    As a developer
    I want beehave to validate that my step decorators follow Gherkin ordering
    So that my tests have correct structure even without .feature files

    @id:9f5d3b2a
    Example: Valid step ordering passes validation
      Given a test with decorators @Given, @When, @Then in order
      When beehave validates step ordering
      Then no ordering violation is reported

    @id:1c8e4a7d
    Example: Invalid step ordering fails validation
      Given a test with decorators @Then, @Given, @When (out of order)
      When beehave validates step ordering
      Then an ordering violation is reported

  Rule: Placeholder names must match function parameters
    As a developer
    I want beehave to validate that every <placeholder> in step text appears as a function parameter
    So that strategy resolution and @Example mapping work correctly

    @id:5b7f2d9e
    Example: All placeholders match function parameters
      Given a step "a user with balance <initial>" and a function with parameter initial
      When beehave validates placeholders
      Then no mismatch is reported

    @id:d3a6c1b8
    Example: Missing function parameter for placeholder
      Given a step "a user with balance <initial>" and a function with no initial parameter
      When beehave validates placeholders
      Then a mismatch is reported: "<initial> not found in function parameters"

  Rule: Progressive adoption allows validation at different levels
    As a developer
    I want to adopt beehave incrementally without requiring .feature files on day one
    So that I can start with decorators only and add traceability later

    @id:8e2f7c4a
    Example: Level 1 — decorators only, no .feature file
      Given a test with @Given, @When, @Then decorators but no .feature file
      When beehave validates the test
      Then step ordering is validated
      And placeholder-parameter matching is validated
      But step text matching is not validated (no .feature file)
      And @id traceability is not validated (no .feature file)

    @id:a4d9b3e6
    Example: Level 2 — decorators with @id traceability
      Given a test with @Given, @When, @Then decorators and a .feature file with matching @id
      When beehave validates the test
      Then step text matching is validated against .feature
      And @id traceability is validated
      And orphan detection is active