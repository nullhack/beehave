from beehave.reporting import render_failure_report


def test_failure_reporting_8e4a2c7f() -> None:
    """Passing test produces no beehave failure report.

    Given a test with @Given, @When, @Then that passes
    When Hypothesis runs the test successfully
    Then no beehave failure report is generated
    And the test runs at full Hypothesis speed with no beehave interception
    """
    result = render_failure_report(
        steps=[{"keyword": "Given", "text": "a passing step"}],
        exception=None,
        counterexample={},
    )
    assert result is None
