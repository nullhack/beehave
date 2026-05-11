Feature: Feature File Mapping and Step Text Matching

  beehave maps .feature files to test modules via Rule structure and validates exact step text matching between .feature files and test decorators.

  Rules (Business):
  - .feature files map to test modules: no Rule → default_test.py, with Rule → <rule_name>_test.py
  - Step text matching is exact — character-for-character after stripping Gherkin keywords and tokenizing <placeholder> variables
  - .feature files are located in docs/features/ by default (configurable in pyproject.toml)
  - One .feature file per feature, one test directory per feature (1:1 mapping)

  Constraints:
  - Validation is collection-time (CLI commands) — zero runtime overhead on passing tests
  - Feature file location is configurable in pyproject.toml under [tool.beehave]

  ## Changes

  | Session | Change |
  |---------|--------|
  | 2026-05-11 | Split from feature_parsing_validation per stakeholder approval |
  | 2026-05-11 | Spec review rework: clarified Then clause (F4), added multi-Rule Example (F5). Deferred: domain model needs Rule entity and TestModule entity (F1, F2) |

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
    Example: Feature with one Rule maps to <rule_name>_test.py
      Given a .feature file "balance_accounting.feature" with Rule "Total calculation"
      When beehave resolves the test module path
      Then it maps to tests/features/balance_accounting/total_calculation_test.py

    @id:cbac8dae
    Example: Feature with multiple Rules maps to multiple test modules
      Given a .feature file "balance_accounting.feature" with Rules "Total calculation" and "Balance check"
      When beehave resolves the test module paths
      Then it maps to tests/features/balance_accounting/total_calculation_test.py
      And it maps to tests/features/balance_accounting/balance_check_test.py

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
      Then a mismatch is reported showing expected "a user with balance <initial>" and actual "a user with an balance <initial>"
