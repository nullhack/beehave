from hypothesis import strategies as st

from beehave.decorators import And, But, Given, Then, When


def test_step_decorator_f3a7c2e1() -> None:
    """All five step decorators annotate a test function.

    Given a test module with strategy variables defined
    When the developer writes a test with @Given, @When, @Then decorators
    Then the test function has __beehave_steps__ metadata attached
    And @Given has applied hypothesis.given() with resolved strategies
    And hypothesis.settings(max_examples=1) is applied
    """

    initial = st.integers(min_value=0)  # noqa: F841
    amount = st.integers(min_value=1)  # noqa: F841
    remaining = st.integers(min_value=0)  # noqa: F841

    @Given("a user with balance <initial>")
    @When("the user spends <amount>")
    @Then("the balance should equal <remaining>")
    def test_balance(initial, amount, remaining):
        assert amount <= initial
        assert remaining == initial - amount

    assert hasattr(test_balance, "__beehave_steps__")
    steps = test_balance.__beehave_steps__
    assert len(steps) == 3
    assert steps[0] == ("Given", "a user with balance <initial>")
    assert steps[1] == ("When", "the user spends <amount>")
    assert steps[2] == ("Then", "the balance should equal <remaining>")

    assert hasattr(test_balance, "_hypothesis_internal_use_settings")
    assert test_balance._hypothesis_internal_use_settings.max_examples == 1


def test_step_decorator_9b4d6e8a() -> None:
    """@And and @But inherit step type from the preceding decorator.

    Given a test with @Given("setup") @And("additional setup") @When("action") @But("contrast")
    When beehave processes the decorator stack at import time
    Then @And is treated as a Given step (continues @Given)
    And @But is treated as a When step (continues @When)
    """

    initial = st.integers(min_value=0)  # noqa: F841

    @Given("setup")
    @And("additional setup")
    @When("action")
    @But("contrast")
    @Then("result is verified")
    def test_with_and_but(initial):
        pass

    steps = test_with_and_but.__beehave_steps__
    assert steps[0] == ("Given", "setup")
    assert steps[1] == ("Given", "additional setup")
    assert steps[2] == ("When", "action")
    assert steps[3] == ("When", "contrast")
    assert steps[4] == ("Then", "result is verified")
