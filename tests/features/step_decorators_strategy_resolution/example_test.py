from hypothesis import strategies as st

from beehave.decorators import Example, Given, Then, When


def test_example_4e1c8b5f() -> None:
    """@Example with keyword arguments.

    Given a test with @Example(initial=100, amount=30, remaining=70)
    When Hypothesis runs the test
    Then the example with initial=100, amount=30, remaining=70 runs first (Phase.explicit)
    And one additional random example runs (Phase.generate)
    """
    initial = st.integers(min_value=0)  # noqa: F841
    amount = st.integers(min_value=1)  # noqa: F841
    remaining = st.integers(min_value=0)  # noqa: F841

    @Given("a user with balance <initial>")
    @When("the user spends <amount>")
    @Then("the balance should equal <remaining>")
    @Example(initial=100, amount=30, remaining=70)
    def test_explicit_keywords(initial, amount, remaining):
        pass

    assert hasattr(test_explicit_keywords, "__beehave_examples__")
    examples = test_explicit_keywords.__beehave_examples__
    assert len(examples) == 1
    assert examples[0].kwargs == {"initial": 100, "amount": 30, "remaining": 70}


def test_example_a97d3e26() -> None:
    """@Example with positional arguments.

    Given a test with @Example(100, 30, 70)
    And steps containing <initial>, <amount>, <remaining> in left-to-right order
    When @Given processes the example
    Then initial=100, amount=30, remaining=70 (positional maps by step text appearance)
    """
    initial = st.integers(min_value=0)  # noqa: F841
    amount = st.integers(min_value=1)  # noqa: F841
    remaining = st.integers(min_value=0)  # noqa: F841

    @Given("a user with balance <initial>")
    @When("the user spends <amount>")
    @Then("the balance should equal <remaining>")
    @Example(100, 30, 70)
    def test_explicit_positional(initial, amount, remaining):
        pass

    assert hasattr(test_explicit_positional, "__beehave_examples__")
    examples = test_explicit_positional.__beehave_examples__
    assert len(examples) == 1
    assert examples[0].args == (100, 30, 70)
