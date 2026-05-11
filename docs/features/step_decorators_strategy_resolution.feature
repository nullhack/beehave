Feature: Step Decorators and Strategy Resolution

  beehave provides Gherkin-style step decorators (@Given, @When, @Then, @And, @But) that attach metadata to test functions and apply Hypothesis @given at import time. Strategy resolution maps <placeholder> names to Hypothesis strategies from module-level variables or @Example value type inference. @Example provides explicit test values from Gherkin Examples tables. @Background provides shared setup fixtures.

  Rules (Business):
  - Step decorators take only a step text string — no inline kwargs, no DSL
  - @Given is the outermost decorator and applies @given at import time
  - @Example values can be keyword (recommended) or positional (shorthand), not mixed
  - Strategy resolution priority: module-level variable → @Example type inference → st.integers() fallback
  - @Background references a fixture function with step decorators; all parameters appear in the test signature

  Constraints:
  - Zero runtime overhead on passing tests — validation is collection-time
  - Core library must not import pytest — runner-agnostic
  - All five decorators are pure structural annotations at the syntax level (only @Given applies @given)

  ## Changes

  | Session | Change |
  |---------|--------|
  | 2026-05-10 | Created: initial feature specification |
  | 2026-05-10 | Removed failure reporting Rules (moved to failure_reporting.feature per decomposition threshold) |
  | 2026-05-10 | Replaced descriptive @id names with 8-char hex IDs per collection_mechanics spec |

  Rule: Step decorator attaches metadata and applies Hypothesis @given
    As a property-based TDD developer
    I want to annotate my test functions with Gherkin step decorators
    So that my tests have Gherkin structure and Hypothesis integration

    @id:f3a7c2e1
    Example: All five step decorators annotate a test function
      Given a test module with strategy variables defined
      When the developer writes a test with @Given, @When, @Then decorators
      Then the test function has __beehave_steps__ metadata attached
      And @Given has applied hypothesis.given() with resolved strategies
      And hypothesis.settings(max_examples=1) is applied

    @id:9b4d6e8a
    Example: @And and @But inherit step type from the preceding decorator
      Given a test with @Given("setup") @And("additional setup") @When("action") @But("contrast")
      When beehave processes the decorator stack at import time
      Then @And is treated as a Given step (continues @Given)
      And @But is treated as a When step (continues @When)

  Rule: Strategy resolution maps placeholder names to Hypothesis strategies
    As a developer
    I want <placeholder> names to resolve to Hypothesis strategies automatically
    So that I don't need explicit registration or configuration

    @id:2c5f1d7e
    Example: Module-level variable resolves a placeholder
      Given a module with "initial = st.integers(min_value=0)"
      And a step "a user with balance <initial>"
      When @Given processes the step at import time
      Then <initial> resolves to the module-level st.integers(min_value=0)

    @id:7a3e8b4c
    Example: @Example value type infers strategy when no module variable exists
      Given a step "the user spends <amount>" with no module-level "amount"
      And @Example(amount=30)
      When @Given processes the step at import time
      Then <amount> resolves to st.integers() (inferred from int type)

    @id:d6f29013
    Example: Unresolved placeholder falls back to st.integers()
      Given a step "the result is <output>" with no module variable and no @Example
      When @Given processes the step at import time
      Then <output> resolves to st.integers() as fallback

  Rule: @Example provides explicit test values in keyword or positional form
    As a developer
    I want to specify concrete test cases from Gherkin Examples tables
    So that deterministic examples run before property-based generation

    @id:4e1c8b5f
    Example: @Example with keyword arguments
      Given a test with @Example(initial=100, amount=30, remaining=70)
      When Hypothesis runs the test
      Then the example with initial=100, amount=30, remaining=70 runs first (Phase.explicit)
      And one additional random example runs (Phase.generate)

    @id:a97d3e26
    Example: @Example with positional arguments
      Given a test with @Example(100, 30, 70)
      And steps containing <initial>, <amount>, <remaining> in left-to-right order
      When @Given processes the example
      Then initial=100, amount=30, remaining=70 (positional maps by step text appearance)

  Rule: @Background provides shared setup for multiple scenarios
    As a developer
    I want to define shared Given/When/Then steps once and reference them from multiple tests
    So that I don't repeat Background setup in every test

    @id:5b2f7c9a
    Example: @Background merges fixture steps and parameters into the test
      Given a background fixture with @Given("a user with balance <initial>") @And("the user is authenticated")
      And a test with @Background(background_balance_accounting) @When("the user spends <amount>") @Then("the balance should equal <remaining>")
      When @Given processes the test at import time
      Then the test's parameter list includes both background (initial) and scenario (amount, remaining) parameters
      And the test's step list includes both background and scenario steps
      And @given includes strategies for all parameters

  