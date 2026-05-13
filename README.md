<div align="center">

<img src="docs/assets/banner.svg" alt="beehave" width="100%"/>

[![Python](https://img.shields.io/badge/python-%E2%89%A53.14-blue?style=for-the-badge)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/beehave?style=for-the-badge)](https://pypi.org/project/beehave/)

**Keep your living documentation and test code in sync — without the step-definition boilerplate.**

</div>

---

**beehave** is a simpler alternative to **behave** and **pytest-bdd**. Instead of writing step definitions that match Gherkin step text to Python functions with `@given`/`@when`/`@then` decorators, beehave links scenarios to tests by **function name** alone. It generates pure [Hypothesis](https://hypothesis.readthedocs.io/) property-based test stubs from your `.feature` files and checks that your test code stays consistent with your spec. Your tests never import beehave — they just use hypothesis.

```bash
pip install beehave
```

---

## How it differs from standard Gherkin tools

Traditional BDD frameworks (behave, pytest-bdd) require **step definitions** — separate Python functions decorated with `@given`/`@when`/`@then` whose text must match the Gherkin step text exactly. This creates fragile coupling, boilerplate, and framework lock-in. beehave eliminates all of that:

- **No step definitions.** The function name **is** the link. `Scenario: guard bee inspects visitor` → `test_guard_bee_inspects_visitor`.
- **No runtime imports.** Your tests import only `hypothesis`. beehave is a dev-time CLI.
- **Property-based by default.** Hypothesis `@given()` strategies are inferred from Examples table types. behave and pytest-bdd are example-only.

To make this work, beehave applies a few constraints beyond standard Gherkin:

| Constraint | Why |
|-----------|-----|
| Titles contain only **letters, digits, and spaces** | They become Python identifiers (`test_...`) and file paths |
| `<placeholder>` names must be valid Python identifiers, not keywords or builtins | They become function parameters |
| `"quoted strings"` and bare numbers in step text are **enforced literals** | `check` verifies they appear as `Constant` nodes in the function body |
| Scenario titles are **globally unique** across all features | One function name = one scenario, everywhere |

---

## Usage

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
      | 50     | 30   | 6     | 35    |

  Rule: Hive defense

    Background:
      Given the entrance has 2 guards

    Scenario: guard bee inspects visitor
      Given a visitor bee with <scent> colony odor
      When the guard inspects the visitor for "floral" scent
      Then the visitor is <outcome>

  Rule: Foraging

    Scenario: forager returns with nectar
      Given a forager bee named <name>
      When the forager returns with <volume> milliliters of nectar
      Then the hive stores <volume> milliliters of nectar
```

### Generate stubs

```bash
beehave generate hive_activity
```

```
tests/features/hive_activity/
├── default_test.py        # top-level scenarios (honey production outline)
├── hive_defense_test.py   # Rule: Hive defense (guard bee)
└── foraging_test.py       # Rule: Foraging (forager returns)
```

```python
# tests/features/hive_activity/default_test.py
from hypothesis import given, example, strategies as st

@example(nectar=100, rate=20, hours=8, honey=80)
@example(nectar=200, rate=25, hours=12, honey=150)
@example(nectar=50, rate=30, hours=6, honey=35)
@given(nectar=st.integers(), rate=st.integers(), hours=st.integers(), honey=st.integers())
def test_honey_production_from_nectar(nectar, rate, hours, honey):
    ...
```

```python
# tests/features/hive_activity/hive_defense_test.py
from hypothesis import given, strategies as st

@given(scent=st.text(), outcome=st.text())
def test_guard_bee_inspects_visitor(scent, outcome):
    ...
```

Note what beehave extracted automatically:

- **`<nectar>`, `<rate>` …** → `@given()` parameters. Strategies inferred from Examples table types (all integers → `st.integers()`).
- **`100`, `20` …** → `@example()` rows from the Examples table.
- **`"floral"`** → enforced literal from step text. `check` verifies it appears in the function body.
- **`2`** (from Rule Background `2 guards`) → enforced literal, inherited by all scenarios in that Rule.
- **`<scent>`, `<outcome>`** → `@given()` parameters. No Examples table, so strategy falls back to `st.text()`.

### Check consistency

You implement the guard test:

```python
@given(scent=st.text(), outcome=st.text())
def test_guard_bee_inspects_visitor(scent, outcome):
    assert "floral" in known_scents()
    assert 2 == guard_count()
    assert scent in ("floral", "citrus")
    assert outcome in ("admitted", "rejected")
```

```bash
beehave check hive_activity    # check one feature
beehave check                  # check all features
```

Remove the `"floral"` assertion and `check` catches it:

```
tests/features/hive_activity/hive_defense_test.py:4: missing-literal: literal '"floral"' not found in function body
```

Remove `<scent>` from the body but keep it as a `@given()` parameter? Still caught — beehave checks the **body only**:

```
tests/features/hive_activity/hive_defense_test.py:4: missing-placeholder: 'scent' not found in function body
```

Rename the scenario? Both sides are reported:

```
docs/features/hive_activity.feature:22: unmapped-scenario: scenario 'guard checks visitor' has no test function
tests/features/hive_activity/hive_defense_test.py:4: unmapped-test: 'test_guard_bee_inspects_visitor' has no matching scenario
```

### Clean up stale functions

```bash
beehave clean hive_activity           # remove unmapped stubs only (safe)
beehave clean hive_activity --force   # remove any unmapped function
```

### List features

```bash
beehave list          # paths and titles
beehave list -v       # include scenario counts, rules, stub status
```

---

## What `check` enforces

| Check | Severity | What it catches |
|-------|----------|-----------------|
| `unmapped-scenario` | error | Scenario has no matching test function |
| `unmapped-test` | error | Test function has no matching scenario |
| `missing-placeholder` | error | `<placeholder>` not referenced in function body |
| `missing-literal` | error | `"string"` or numeric literal not in function body |
| `example-mismatch` | error | Examples row has no matching `@example()` or vice versa |
| `misplaced-test` | warning | Function in wrong file (e.g., after Rule removal) |

Warnings exit 0. Errors exit 1. Stubs (bodies with only `pass` or `...`) skip body enforcement until you implement them.

---

## How it maps

- **Scenario title → function name:** `Honey Production From Nectar` → `test_honey_production_from_nectar`. Globally unique across all features.
- **Rule → test file:** Top-level scenarios go to `default_test.py`. Scenarios inside a Rule go to `<rule>_test.py`.
- **Feature title → directory:** `Hive Activity` → `tests/features/hive_activity/`.
- **Strategy inference:** Examples table column values are typed — all integers → `st.integers()`, all floats → `st.floats()`, all booleans → `st.booleans()`, else → `st.text()`.
- **Background merging:** Feature Background applies to all scenarios. Rule Background applies to that Rule's scenarios only. Background steps cannot contain `<placeholders>`.
- **Literal extraction:** `"quoted strings"` and numeric tokens in step text are enforced as `Constant` AST nodes in the function body.

---

## Configuration

```toml
# pyproject.toml
[tool.beehave]
features_dir = "docs/features"
tests_dir = "tests/features"
default_strategy = "text"
background_check_numeric = true
background_check_string = true
```

| Option | Default | Description |
|--------|---------|-------------|
| `features_dir` | `docs/features` | Where `.feature` files live |
| `tests_dir` | `tests/features` | Where generated tests go |
| `default_strategy` | `text` | Fallback strategy for unknown placeholders |
| `background_check_numeric` | `true` | Enforce numeric literals from Background steps |
| `background_check_string` | `true` | Enforce string literals from Background steps |

## License

MIT
