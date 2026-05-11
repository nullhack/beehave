from beehave.reporting import render_step_text


def test_failure_reporting_b9d4a7c3() -> None:
    """Placeholder tokens rendered with actual values from counterexample.

    Given a step "the balance should equal <initial> - <amount>"
    And the test fails with initial=5, amount=10
    When the failure report is rendered
    Then the step text becomes "the balance should equal 5 - 10"
    And the Hypothesis counterexample values are visible in the Gherkin report
    """
    result = render_step_text(
        "the balance should equal <initial> - <amount>",
        {"initial": 5, "amount": 10},
    )
    assert result == "the balance should equal 5 - 10"
