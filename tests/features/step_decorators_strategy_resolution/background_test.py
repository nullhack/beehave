from hypothesis import strategies as st

from beehave.decorators import And, Background, Given, Then


def test_background_5b2f7c9a() -> None:
    """@Background merges fixture steps and parameters into the test.

    Given a background fixture with @Given("a user with balance <initial>") @And("the user is authenticated")
    And a test with @Background(background_balance_accounting) @When("the user spends <amount>") @Then("the balance should equal <remaining>")
    When @Given processes the test at import time
    Then the test's parameter list includes both background (initial) and scenario (amount, remaining) parameters
    And the test's step list includes both background and scenario steps
    And @given includes strategies for all parameters
    """

    @Given("a user with balance <initial>")
    @And("the user is authenticated")
    def background_balance_accounting(initial):
        pass

    initial = st.integers(min_value=0)  # noqa: F841
    amount = st.integers(min_value=1)  # noqa: F841
    remaining = st.integers(min_value=0)  # noqa: F841

    @Background(background_balance_accounting)
    @Given("the user spends <amount>")
    @Then("the balance should equal <remaining>")
    def test_with_background(initial, amount, remaining):
        pass

    steps = test_with_background.__beehave_steps__

    assert ("Given", "a user with balance <initial>") in steps
    assert ("Given", "the user is authenticated") in steps
    assert ("Then", "the balance should equal <remaining>") in steps

    assert hasattr(test_with_background, "hypothesis")
