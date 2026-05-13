<div align="center">

<img src="docs/assets/banner.svg" alt="beehave" width="100%"/>

<br/><br/>

[![Python](https://img.shields.io/badge/python-%E2%89%A53.14-blue?style=for-the-badge)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/beehave?style=for-the-badge)](https://pypi.org/project/beehave/)

**Gherkin features in, Hypothesis tests out. Zero coupling.**

</div>

---

You write `.feature` files. Your tests use `hypothesis`. They need to stay in sync — every scenario maps to a function, every `<placeholder>` to a parameter, every `"literal"` to a body assertion. Do it by hand and it drifts. Add a BDD framework and your tests depend on it forever.

**beehave generates pure Hypothesis test stubs from Gherkin and checks they stay consistent. No `import beehave` in your test code. Ever.**

---

## Quick start

```bash
pip install beehave
```

### Write a feature

```gherkin
# docs/features/hive_activity.feature
Feature: Hive Activity

  Background:
    Given the hive is active

  Scenario Outline: honey production from nectar
    Given the hive has <nectar> grams of nectar
    And the evaporation rate is <rate> percent
    When the bees fan their wings for <hours> hours
    Then the hive produces <honey> grams of honey

    Examples:
      | nectar | rate | hours | honey |
      | 100    | 20   | 8     | 80    |
      | 200    | 25   | 12    | 150   |

  Rule: Hive defense

    Background:
      Given the entrance has 2 guards

    Scenario: guard bee inspects visitor
      Given a visitor bee with <scent> colony odor
      When the guard inspects the visitor for "floral" scent
      Then the visitor is <outcome>
```

### Generate

```bash
beehave generate hive_activity
```

Produces `tests/features/hive_activity/default_test.py`:

```python
from hypothesis import given, example, settings, strategies as st

settings.register_profile("beehave", max_examples=1)
settings.load_profile("beehave")

@example(nectar=100, rate=20, hours=8, honey=80)
@example(nectar=200, rate=25, hours=12, honey=150)
@given(nectar=st.integers(), rate=st.integers(), hours=st.integers(), honey=st.integers())
def test_honey_production_from_nectar(nectar, rate, hours, honey):
    ...

@given(scent=st.text(), outcome=st.text())
def test_guard_bee_inspects_visitor(scent, outcome):
    ...
```

Note what beehave extracted:

| Source | Extracted | Where it ends up |
|--------|-----------|-----------------|
| `<nectar>`, `<rate>` … | Placeholders | `@given()` parameters, inferred `st.integers()` from Examples |
| `100`, `20` … | Numeric literals (from Examples) | `@example()` rows |
| `"floral"` | String literal (from step text) | Enforced as `Constant` in body |
| `2` (from Rule Background) | Numeric literal (from Background) | Enforced as `Constant` in body |

### Check

You implement the guard test:

```python
@given(scent=st.text(), outcome=st.text())
def test_guard_bee_inspects_visitor(scent, outcome):
    assert "floral" in known_scents()
    assert 2 == guard_count()
    assert outcome in ("admitted", "rejected")
```

```bash
beehave check hive_activity
```

Clean. Now remove the `"floral"` check:

```bash
beehave check hive_activity
```

```
tests/features/hive_activity/default_test.py:9: missing-literal: literal '"floral"' not found in function body
```

Rename the scenario title? `check` reports both sides:

```
docs/features/hive_activity.feature:20: unmapped-scenario: scenario 'guard checks visitor' has no test function
tests/features/hive_activity/default_test.py:9: unmapped-test: 'test_guard_bee_inspects_visitor' has no matching scenario
```

### Clean

```bash
beehave clean hive_activity           # remove unmapped stubs
beehave clean hive_activity --force   # remove any unmapped function
```

---

## Commands

```
beehave generate <feature>            # generate stubs for one feature
beehave check [<feature>]             # check consistency (all or one)
beehave clean <feature> [--force]     # remove unmapped test functions
```

## What check enforces

| Error type | Trigger |
|------------|---------|
| `unmapped-scenario` | Scenario has no matching `test_` function |
| `unmapped-test` | Test function has no matching scenario |
| `missing-placeholder` | `<placeholder>` not in function signature |
| `missing-literal` | String `"…"` or numeric literal not in function body |
| `example-mismatch` | Examples row has no matching `@example()` (or vice versa) |

Stubs (bodies containing only `pass` or `...`) skip body enforcement — they pass `check` until you implement them.

## How it works

**Scenario → function name:** trim → collapse spaces → underscores → prepend `test_`. Titles must be globally unique across all features.

**Strategy inference:** Scenario Outline Examples table values are typed. All integers → `st.integers()`, all floats → `st.floats()`, all booleans → `st.booleans()`, mixed → `st.text()`. Plain scenarios default to `st.text()`.

**Background merging:** Feature Background → all scenarios. Rule Background → only scenarios in that Rule. Background literals are enforced on every scenario in scope.

**Literal extraction:** `"quoted strings"` and bare numeric tokens (`100`, `3`) in step text become literals that `check` verifies exist as `Constant` AST nodes in the function body.

**Pipeline:**

```
.feature → gherkin parse → ScenarioInfo dict
                              ↘
                               check → violations
                              ↗
.py → AST discover → TestInfo dict
```

No cache. No state. No runtime coupling.

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

## License

MIT
