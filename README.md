<div align="center">
  <img src="https://raw.githubusercontent.com/nullhack/beehave/main/docs/assets/banner.svg" alt="beehave" width="860" height="200">
</div>

**beehave** — A thin layer on [Hypothesis](https://hypothesis.readthedocs.io/) for Gherkin-style BDD testing with vocabulary enforcement.

One function. One scenario. No step definition sprawl.

---

## Why

Existing BDD frameworks split a single scenario across multiple step definition functions with brittle string matching. beehave gives you one test function per scenario, `@id`-based traceability, and collection-time vocabulary validation — all on top of Hypothesis.

## Install

```bash
pip install beehave
```

Requires Python 3.14+ and Hypothesis 6+.

## Quick start

Write a feature file:

```gherkin
# docs/features/wallet.feature
Feature: Wallet balance

  @id: a1b2c3d4
  Scenario: spending reduces balance
    Given a user with balance <initial>
    When the user spends <amount>
    Then the balance should equal <remaining>
```

Generate the test stub:

```python
# Generated in tests/features/wallet/default_test.py
from beehave.decorators import Given, When, Then, Example
from hypothesis import strategies as st

initial = st.integers(min_value=0)
amount = st.integers(min_value=1)
remaining = st.integers(min_value=0)

@Given("a user with balance <initial>")
@When("the user spends <amount>")
@Then("the balance should equal <remaining>")
def test_wallet_balance_a1b2c3d4(initial, amount, remaining):
    ...
```

Fill in the body and run with pytest:

```python
def test_wallet_balance_a1b2c3d4(initial, amount, remaining):
    assert amount <= initial
    assert remaining == initial - amount
```

Hypothesis generates values for `<initial>`, `<amount>`, and `<remaining>`. Vocabulary enforcement validates your decorator strings match the `.feature` file at collection time.

## Features

### Gherkin step decorators

`@Given`, `@When`, `@Then`, `@And`, `@But` — decorate any test function. They compose with Hypothesis `@given` under the hood.

### Scenario Outline + Examples

```gherkin
@id: e5f6a7b8
Scenario Outline: transfer between accounts
  Given account A has <balance_a>
  And account B has <balance_b>
  When <amount> is transferred from A to B
  Then account A has <result_a>
  And account B has <result_b>

  Examples:
    | balance_a | balance_b | amount | result_a | result_b |
    | 100       | 50        | 30     | 70       | 80       |
    | 200       | 0         | 50     | 150      | 50       |
```

Each Examples row generates an `@Example` test case with concrete values.

### `<placeholder>` in any scenario

Use `<name>` in step text to declare a Hypothesis-driven parameter:

```gherkin
@id: c9d0e1f2
Scenario: flexible search
  Given a hive with <colony_size> bees
  When they collect <nectar_units> units of nectar
  Then the honey yield is calculated
```

Wrap in single quotes to force string type: `'<colony_name>'` → `st.text()` strategy.

### Vocabulary enforcement

At test collection time, beehave checks that every `@Given`/`@When`/`@Then`/`@And`/`@But` decorator string matches the corresponding step text in your `.feature` files. Mismatches are reported immediately — no silent drift.

### `@id` traceability

Every scenario gets a unique `@id` tag. Test functions are named `test_<feature>_<id>`, giving you a 1:1 link between Gherkin scenarios and test code. Scenario Outline rows get deterministic IDs derived from the heading ID and row index.

## CLI

beehave provides four commands (import and call from Python):

```python
from beehave.cli import sync, generate, fix, clean
```

| Command | Purpose |
|---------|---------|
| `sync(path)` | Assign `@id` tags to untagged scenarios *(coming soon)* |
| `generate(name)` | Create test stubs for scenarios that lack them |
| `fix(name)` | Correct decorator text to match `.feature` step text |
| `clean(name)` | Remove orphan test functions with no matching scenario |

## Architecture

- **`beehave.decorators`** — `@Given`, `@When`, `@Then`, `@And`, `@But`, `@Example`, `@Background`. Compose with Hypothesis at import time.
- **`beehave.traceability`** — Gherkin parser, `@id` extraction, Scenario Outline expansion, placeholder detection.
- **`beehave.cli`** — `generate`, `fix`, `clean` commands. Vocabulary alignment via SequenceMatcher.
- **`beehave.validation`** — Collection-time checks: decorator/feature step matching, orphan detection.

Runner-agnostic core. pytest is supported out of the box; any Hypothesis-compatible runner works.

## License

MIT — see [LICENSE](LICENSE).
