import pytest


@pytest.mark.skip(reason="not yet implemented")
def test_failure_reporting_3f7b9d4a() -> None:
    """ValueError in setup is attributed to @Given by line-number heuristic.

    Given a test where User(balance=-1) raises ValueError during setup
    When the exception occurs in the Given step region
    Then the failure report shows the @Given step with ✗ and the exception message
    And @When and @Then steps show "(not reached)"
    """
    raise NotImplementedError


@pytest.mark.skip(reason="not yet implemented")
def test_failure_reporting_6e2c8b1f() -> None:
    """RuntimeError in action is attributed to @When by line-number heuristic.

    Given a test where user.spend() raises RuntimeError during action
    When the exception occurs in the When step region
    Then the failure report shows @Given ✓, @When ✗ with exception
    And @Then steps show "(not reached)"
    """
    raise NotImplementedError
