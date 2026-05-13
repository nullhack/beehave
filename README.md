<div align="center">

<img src="docs/assets/banner.svg" alt="beehave" width="100%"/>

<br/><br/>

[![Python](https://img.shields.io/badge/python-%E2%89%A53.14-blue?style=for-the-badge)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/beehave?style=for-the-badge)](https://pypi.org/project/beehave/)

**Gherkin features in, Hypothesis tests out. Zero coupling.**

</div>

---

You write `.feature` files. Your test runner imports `hypothesis`. Somehow they need to stay in sync — every scenario maps to a test function, every placeholder to a parameter, every literal to a body assertion. Do it by hand and it drifts. Add a BDD framework and now your tests depend on it forever.

**beehave generates pure Hypothesis test stubs from Gherkin and checks they stay consistent — without ever appearing in your test code.**

Generated tests import only `hypothesis`. There is no `import beehave` anywhere at runtime. Change a feature title, add a placeholder, remove an example row — `beehave check` tells you exactly what broke and where.

---

## Quick start

```bash
pip install beehave
```

Write a feature file:

```gherkin
# docs/features/bank_account.feature
Feature: Bank Account

  Scenario: deposit increases balance
    Given an account with "USD" currency
    And a balance of 100
    When the depositor deposits 50
    Then the balance is 150
```

Generate the test stub:

```bash
beehave generate bank_account
```

```python
# tests/features/bank_account/default_test.py
from hypothesis import given, settings, strategies as st

settings.register_profile("beehave", max_examples=1)
settings.load_profile("beehave")

@given(currency=st.text(), balance=st.integers(), amount=st.integers(), total=st.integers())
def test_deposit_increases_balance(currency, balance, amount, total):
    ...
```

Fill in the body. Now change the feature — rename the scenario, add a `<fee>` placeholder, swap `"USD"` for `"EUR"`. Run:

```bash
beehave check bank_account
```

```
docs/features/bank_account.feature:4: unmapped-scenario: scenario 'deposit increases balance' has no test function
tests/features/bank_account/default_test.py:7: unmapped-test: 'test_deposit_increases_balance' has no matching scenario
```

Fix the drift. Re-check. Clean slate.

## Commands

```
beehave generate <feature>            # stub out test functions for a feature
beehave check [<feature>]             # verify scenarios ↔ tests are in sync
beehave clean <feature> [--force]     # remove unmapped test functions
```

| Command | What it does |
|---------|-------------|
| `generate` | Parses `.feature` → emits Hypothesis stubs. Infers `st.integers()` etc. from Examples table types. Appends only missing functions to existing files. |
| `check` | Dict-joins parsed scenarios with AST-discovered test functions. Reports mismatches in `<path>:<line>: <error_type>: <message>` format. Exit `1` if any violations. |
| `clean` | Removes unmapped test functions. Safe by default (stubs only). `--force` removes any. |

## Scenario Outline with Examples

```gherkin
Scenario Outline: transfer between accounts
  Given a source balance of <source>
  And a target balance of <target>
  When the sender transfers <amount>
  Then the source balance is <source_remain>
  And the target balance is <target_remain>

  Examples:
    | source | target | amount | source_remain | target_remain |
    | 100    | 50     | 30     | 70            | 80            |
    | 0      | 200    | 0      | 0             | 200           |
```

```bash
beehave generate transfer
```

```python
@example(source=100, target=50, amount=30, source_remain=70, target_remain=80)
@example(source=0, target=200, amount=0, source_remain=0, target_remain=200)
@given(source=st.integers(), target=st.integers(), amount=st.integers(),
       source_remain=st.integers(), target_remain=st.integers())
def test_transfer_between_accounts(source, target, amount, source_remain, target_remain):
    ...
```

`@example` rows run deterministically. `@given` adds random Hypothesis cases on top.

## What check catches

| Error type | Trigger |
|------------|---------|
| `unmapped-scenario` | Scenario has no matching `test_` function |
| `unmapped-test` | Test function has no matching scenario |
| `missing-placeholder` | `<placeholder>` not in function signature |
| `missing-literal` | String or numeric literal not in function body |
| `example-mismatch` | Examples row has no matching `@example()` (or vice versa) |

## Configuration

`pyproject.toml`:

```toml
[tool.beehave]
features_dir = "docs/features"
tests_dir = "tests/features"
default_strategy = "text"
max_examples = 1
background_check_numeric = true
background_check_string = true
```

| Option | Default | Description |
|--------|---------|-------------|
| `features_dir` | `docs/features` | Where `.feature` files live |
| `tests_dir` | `tests/features` | Where generated tests go |
| `default_strategy` | `text` | Fallback strategy for unknown placeholders |
| `max_examples` | `1` | Hypothesis `max_examples` for `@given()` functions |
| `background_check_numeric` | `true` | Enforce numeric literals from Background steps |
| `background_check_string` | `true` | Enforce string literals from Background steps |

## How it works

```
.feature → gherkin parse → ScenarioInfo dict
                              ↘
                               check → violations
                              ↗
.py → AST discover → TestInfo dict
```

- Scenario titles map to function names: trim → collapse spaces → underscores → prepend `test_`
- Scenario titles must be **globally unique** across all features
- One `.feature` file → one test directory → one `default_test.py`
- No cache, no state, no runtime coupling — beehave is a build-time tool

## License

MIT
