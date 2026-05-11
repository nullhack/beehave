import pytest


@pytest.mark.skip(reason="not yet implemented")
def test_failure_reporting_1d6b3f9e() -> None:
    """AssertionError is attributed to the failing @Then step.

    Given a test with @Given("a user with balance <initial>") @When("the user spends <amount>") @Then("the balance should equal <remaining>")
    And the test fails with initial=5, amount=10, remaining=-5
    When the assert statement in the Then step fails
    Then the failure report shows:
        Given a user with balance 5 ✓
        When the user spends 10 ✓
        Then the balance should equal -5 ✗ (AssertionError)
    """
    raise NotImplementedError


@pytest.mark.skip(reason="not yet implemented")
def test_failure_reporting_c5a8e27d() -> None:
    """Multiple @Then steps — first failure stops, subsequent marked not reached.

    Given a test with @Then("the balance equals <remaining>") @But("no fee is charged")
    And the first @Then fails
    When the assertion fails in the first @Then
    Then the first @Then shows ✗
    And @But("no fee is charged") shows "(not reached)"
    """
    raise NotImplementedError
