# beehave

A thin layer on [Hypothesis](https://hypothesis.readthedocs.io/) for Gherkin-style BDD testing with vocabulary enforcement.

## Installation

```bash
pip install beehave
```

## Quick start

```python
from hypothesis import strategies as st
from beehave import Given, When, Then, And, Example, Background

initial = st.integers(min_value=0)
amount = st.integers(min_value=1)
remaining = st.integers(min_value=0)

@Given("a user with balance <initial>")
@When("the user spends <amount>")
@Then("the balance should equal <remaining>")
def test_balance(initial, amount, remaining):
    assert amount <= initial
    assert remaining == initial - amount
```

## License

MIT — see [LICENSE](LICENSE).