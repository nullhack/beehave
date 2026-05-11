Feature: Failure Reporting

  beehave renders Gherkin-readable failure reports from Hypothesis counterexamples. When a beehave-decorated test fails, step decorators serve as report templates, with <placeholder> values filled in from the counterexample. The Then-failed heuristic attributes assertion failures to @Then; the line-number heuristic attributes non-assertion exceptions to @Given or @When.

  Rules (Business):
  - Failure reporting activates only on test failure — zero overhead on passing tests
  - The Then-failed heuristic: assertion failures are always attributed to @Then or @But
  - The line-number heuristic: non-assertion exceptions are attributed to @Given or @When by body line order
  - Step text with <placeholder> tokens is rendered with actual values from the counterexample
  - The Gherkin report is supplementary — the Python traceback always shows the exact failing line

  Constraints:
  - Reporting uses Hypothesis's report_example callback (runner-agnostic)
  - Core library must not import pytest for reporting
  - Future pytest plugin can enhance output formatting

  ## Changes

  | Session | Change |
  |---------|--------|
  | 2026-05-10 | Created: initial feature specification |
  | 2026-05-10 | Replaced descriptive @id names with 8-char hex IDs per collection_mechanics spec |

  Rule: Passing tests show no failure report
    As a developer
    I want passing tests to have zero overhead from beehave reporting
    So that my test suite runs at full Hypothesis speed

    @id:8e4a2c7f
    Example: Passing test produces no beehave report
      Given a test with @Given, @When, @Then that passes
      When Hypothesis runs the test successfully
      Then no beehave failure report is generated
      And the test runs at full Hypothesis speed with no beehave interception

  Rule: Assertion failures are attributed to @Then
    As a QA engineer
    I want to see which Gherkin step failed when an assertion fails
    So that I can understand failures in stakeholder-readable terms

    @id:1d6b3f9e
    Example: AssertionError attributed to the failing @Then
      Given a test with @Given("a user with balance <initial>") @When("the user spends <amount>") @Then("the balance should equal <remaining>")
      And the test fails with initial=5, amount=10, remaining=-5
      When the assert statement in the Then step fails
      Then the failure report shows:
        Given a user with balance 5 ✓
        When the user spends 10 ✓
        Then the balance should equal -5 ✗ (AssertionError)

    @id:c5a8e27d
    Example: Multiple @Then steps — first failure stops, subsequent marked not reached
      Given a test with @Then("the balance equals <remaining>") @But("no fee is charged")
      And the first @Then fails
      When the assertion fails in the first @Then
      Then the first @Then shows ✗
      And @But("no fee is charged") shows "(not reached)"

  Rule: Non-assertion exceptions are attributed by line-number heuristic
    As a developer
    I want non-assertion exceptions to be attributed to the correct Gherkin phase
    So that I can quickly identify whether the failure is in setup or action

    @id:3f7b9d4a
    Example: ValueError in setup attributed to @Given
      Given a test where User(balance=-1) raises ValueError during setup
      When the exception occurs in the Given step region
      Then the failure report shows the @Given step with ✗ and the exception message
      And @When and @Then steps show "(not reached)"

    @id:6e2c8b1f
    Example: RuntimeError in action attributed to @When
      Given a test where user.spend() raises RuntimeError during action
      When the exception occurs in the When step region
      Then the failure report shows @Given ✓, @When ✗ with exception
      And @Then steps show "(not reached)"

  Rule: Placeholder values are rendered from Hypothesis counterexample
    As a QA engineer
    I want to see the actual values that caused the failure
    So that I can understand what input triggered the bug

    @id:b9d4a7c3
    Example: All <placeholder> tokens rendered with actual values
      Given a step "the balance should equal <initial> - <amount>"
      And the test fails with initial=5, amount=10
      When the failure report is rendered
      Then the step text becomes "the balance should equal 5 - 10"
      And the Hypothesis counterexample values are visible in the Gherkin report