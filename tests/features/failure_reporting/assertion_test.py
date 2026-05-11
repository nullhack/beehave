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
    from beehave.reporting import StepStatus, render_failure_report

    steps = [
        ("Given", "a user with balance <initial>"),
        ("When", "the user spends <amount>"),
        ("Then", "the balance should equal <remaining>"),
    ]
    exception = AssertionError("assert failed")
    counterexample = {"initial": 5, "amount": 10, "remaining": -5}

    report = render_failure_report(steps, exception, counterexample)

    assert report is not None
    assert report.is_assertion_error is True
    assert report.failed_step_index == 2
    assert len(report.steps) == 3

    # Given step — PASSED
    assert report.steps[0].step_keyword == "Given"
    assert report.steps[0].step_text == "a user with balance 5"
    assert report.steps[0].status == StepStatus.PASSED
    assert report.steps[0].exception_message is None

    # When step — PASSED
    assert report.steps[1].step_keyword == "When"
    assert report.steps[1].step_text == "the user spends 10"
    assert report.steps[1].status == StepStatus.PASSED
    assert report.steps[1].exception_message is None

    # Then step — FAILED
    assert report.steps[2].step_keyword == "Then"
    assert report.steps[2].step_text == "the balance should equal -5"
    assert report.steps[2].status == StepStatus.FAILED
    assert report.steps[2].exception_message == "assert failed"


def test_failure_reporting_c5a8e27d() -> None:
    """Multiple @Then steps — first failure stops, subsequent marked not reached.

    Given a test with @Then("the balance equals <remaining>") @But("no fee is charged")
    And the first @Then fails
    When the assertion fails in the first @Then
    Then the first @Then shows ✗
    And @But("no fee is charged") shows "(not reached)"
    """
    from beehave.reporting import StepStatus, render_failure_report

    steps = [
        ("Then", "the balance equals <remaining>"),
        ("But", "no fee is charged"),
    ]
    exception = AssertionError("assertion failed")
    counterexample = {"remaining": -5}

    report = render_failure_report(
        steps, exception, counterexample, failed_step_index=0
    )

    assert report.failed_step_index == 0
    assert report.steps[0].status == StepStatus.FAILED
    assert report.steps[1].status == StepStatus.NOT_REACHED
    assert report.steps[1].step_text == "no fee is charged"
