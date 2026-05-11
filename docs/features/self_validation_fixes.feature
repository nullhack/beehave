Feature: Self-Validation Fixes
  Fixes discovered during self-validation of beehave's generate() command and strategy resolution.

  Rules (Business):
  - generate() text output shows the actual file path for each created or appended stub
  - generate() produces one import block per file, even when appending multiple scenarios
  - generate() creates test directories as proper Python packages with __init__.py
  - generate() produces stubs that are clearly unimplemented (skipped, not passing)
  - generate() includes step decorators matching .feature Gherkin steps in each stub
  - Strategy resolution warns the developer when falling back to st.integers()

  Constraints:
  - Fixes must not break existing traceability_generate_core or traceability_generate_modes tests
  - Fixes must not break existing step_decorators_strategy_resolution tests
  - Runner-agnostic principle applies to the core library (beehave/*), not to generated test stubs — stubs target pytest by convention

  ## Changes

  | Session | Change |
  |---------|--------|
  | IN_20260511 | 6 pain points identified from self-validation exercise |

  Rule: generate() output is observable

    @id:f1a2b3c4
    Example: Text output shows created file path
      Given a feature file "hive_tracking.feature" with 2 scenarios
      When beehave generates stubs in text mode
      Then the output contains "Created tests/features/hive_tracking/default_test.py"
      And the output contains the @id for each scenario

    @id:d5e6f7a8
    Example: Appending shows file path with scenario @id
      Given a feature file "hive_tracking.feature" with 3 scenarios and an existing stub for the first
      When beehave generates stubs in text mode
      Then the output contains "Appended to tests/features/hive_tracking/default_test.py"
      And the output contains the @id for the new scenarios

  Rule: generate() produces clean Python files

    @id:b9c0d1e2
    Example: Multiple scenarios produce one import block
      Given a feature file "hive_tracking.feature" with 3 scenarios
      When beehave generates stubs
      Then the output file contains "from beehave.decorators import" exactly once
      And each scenario has its own test function

    @id:f3a4b5c6
    Example: Generated test directory has __init__.py
      Given a feature file "hive_tracking.feature" with 1 scenario
      When beehave generates stubs
      Then tests/features/hive_tracking/__init__.py exists
      And tests/features/hive_tracking/default_test.py exists

  Rule: generate() produces clearly unimplemented stubs

    @id:d7e8f9a0
    Example: Generated stubs are skipped by pytest
      Given a feature file "hive_tracking.feature" with 1 scenario
      When beehave generates stubs
      Then pytest collects the stub as SKIPPED
      And the stub body raises NotImplementedError

  Rule: generate() includes step decorators in stubs

    @id:b1c2d3e4
    Example: Stub has decorators matching .feature Gherkin steps
      Given a feature file "hive_tracking.feature" with a scenario having Given/When/Then steps
      When beehave generates stubs
      Then the stub function has @Given, @When, @Then decorators matching the feature steps
      And the stub function parameters include the <placeholder> names from the steps

  Rule: Strategy fallback is visible to developers

    @id:a5b6c7d8
    Example: Missing strategy variable produces a warning
      Given a test using <quantity> placeholder with no quantity_strategy defined
      When beehave resolves strategies at import time
      Then a UserWarning is emitted mentioning "quantity" and "st.integers() fallback"
