from beehave.reporting import StepStatus, render_failure_report


def test_failure_reporting_3f7b9d4a() -> None:
    """ValueError in setup is attributed to @Given by line-number heuristic.

    Given a test where User(balance=-1) raises ValueError during setup
    When the exception occurs in the Given step region
    Then the failure report shows the @Given step with ✗ and the exception message
    And @When and @Then steps show "(not reached)"
    """
    steps = [
        ("Given", "a user with balance <initial>"),
        ("When", "the user spends <amount>"),
        ("Then", "the balance should equal <remaining>"),
    ]
    exception = ValueError("balance cannot be negative")
    counterexample = {"initial": -1}

    report = render_failure_report(
        steps,
        exception,
        counterexample,
        failed_step_index=0,
    )

    assert report.failed_step_index == 0
    assert report.is_assertion_error is False

    assert report.steps[0].status == StepStatus.FAILED
    assert "balance cannot be negative" in report.steps[0].exception_message

    assert report.steps[1].status == StepStatus.NOT_REACHED
    assert report.steps[2].status == StepStatus.NOT_REACHED


def test_failure_reporting_6e2c8b1f() -> None:
    """RuntimeError in action is attributed to @When by line-number heuristic.

    Given a test where user.spend() raises RuntimeError during action
    When the exception occurs in the When step region
    Then the failure report shows @Given ✓, @When ✗ with exception
    And @Then steps show "(not reached)"
    """
    steps = [
        ("Given", "a user with balance <initial>"),
        ("When", "the user spends <amount>"),
        ("Then", "the balance should equal <remaining>"),
    ]
    exception = RuntimeError("insufficient funds")
    counterexample = {"initial": 5, "amount": 10}

    report = render_failure_report(
        steps,
        exception,
        counterexample,
        failed_step_index=1,
    )

    assert report.failed_step_index == 1
    assert report.is_assertion_error is False

    assert report.steps[0].status == StepStatus.PASSED
    assert report.steps[0].step_text == "a user with balance 5"

    assert report.steps[1].status == StepStatus.FAILED
    assert "insufficient funds" in report.steps[1].exception_message

    assert report.steps[2].status == StepStatus.NOT_REACHED
