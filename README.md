<p align="center">
  <img src="docs/assets/banner.svg" alt="beehave — BDD living documentation in sync" width="600">
</p>

# beehave

**BDD living documentation in sync.**

beehave is a CLI tool that generates pure [Hypothesis](https://hypothesis.readthedocs.io/) test stubs from [Gherkin](https://cucumber.io/docs/gherkin/) `.feature` files and keeps them consistent — with zero runtime coupling.

Generated tests import only `hypothesis`. beehave itself never appears in your test code.

## Install

```bash
pip install beehave
```

Requires Python 3.14+.

## Quick start

### 1. Write a feature file

```gherkin
# docs/features/hive_activity.feature
Feature: Hive Activity

  Background:
    Given the hive is active

  Example: forager returns with nectar
    Given a forager bee named <name>
    When the forager returns with <volume> milliliters of nectar
    Then the hive stores <volume> milliliters of nectar

  Scenario Outline: honey production from nectar
    Given the hive has <nectar> grams of nectar
    And the evaporation rate is <rate> percent
    When the bees fan their wings for <hours> hours
    Then the hive produces <honey> grams of honey

    Examples:
      | nectar | rate | hours | honey |
      | 100    | 20   | 8     | 80    |
      | 200    | 25   | 12    | 150   |
```

### 2. Generate test stubs

```bash
beehave generate hive_activity
```

Produces `tests/features/hive_activity/default_test.py`:

```python
from hypothesis import given, example, settings, strategies as st

settings.register_profile("beehave", max_examples=1)
settings.load_profile("beehave")

@given(name=st.text(), volume=st.text())
def test_forager_returns_with_nectar(name, volume):
    ...

@example(nectar=100, rate=20, hours=8, honey=80)
@example(nectar=200, rate=25, hours=12, honey=150)
@given(nectar=st.integers(), rate=st.integers(), hours=st.integers(), honey=st.integers())
def test_honey_production_from_nectar(nectar, rate, hours, honey):
    ...
```

### 3. Check consistency

```bash
beehave check                # check all features
beehave check hive_activity  # check a single feature
```

Reports violations in `<path>:<line>: <error_type>: <message>` format. Exits `1` if any violations found.

### 4. Clean up unmapped functions

```bash
beehave clean hive_activity           # remove stub unmapped functions
beehave clean hive_activity --force   # remove any unmapped function
```

## How it works

beehave has three commands, each composable as a function API:

| Command | What it does |
|---------|-------------|
| `generate` | Parses `.feature` files, emits Hypothesis stubs. Infers strategies from Examples table types. |
| `check` | Dict-joins parsed scenarios with AST-discovered test functions. Reports mismatches. |
| `clean` | Removes unmapped test functions. Safe by default (stubs only). |

**Pipeline:** `.feature` → `gherkin` parse → `ScenarioInfo` dict → join with `discover` → `TestInfo` dict → `check`/`generate`/`clean`

### Function name derivation

Scenario titles map deterministically to test function names:

1. Trim whitespace
2. Collapse spaces to underscores
3. Prepend `test_`

`"forager returns with nectar"` → `test_forager_returns_with_nectar`

Scenario titles must be **globally unique** across all features.

### Strategy inference

For Scenario Outlines with Examples tables, beehave infers Hypothesis strategies from column values:

| Column values | Strategy |
|---------------|----------|
| All integers | `st.integers()` |
| All floats | `st.floats()` |
| All booleans | `st.booleans()` |
| Mixed / text | `st.text()` |

For plain scenarios, the default strategy is `st.text()` (configurable).

### Literal enforcement

String literals in step text (both `"..."` and `'...'`) and numeric literals are extracted and enforced:

```gherkin
Given a color "amber"
Given 3 items
```

`check` verifies that the constants `"amber"` and `3` appear in the test function body.

## Configuration

Add a `[tool.beehave]` section to `pyproject.toml`:

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
| `features_dir` | `docs/features` | Directory containing `.feature` files |
| `tests_dir` | `tests/features` | Directory for generated test files |
| `default_strategy` | `text` | Fallback strategy for unknown placeholders |
| `max_examples` | `1` | Hypothesis profile max_examples |
| `background_check_numeric` | `true` | Enforce numeric literals in Background steps |
| `background_check_string` | `true` | Enforce string literals in Background steps |

## Error types

| Error type | Meaning |
|------------|---------|
| `unmapped-scenario` | Scenario has no matching test function |
| `unmapped-test` | Test function has no matching scenario |
| `missing-placeholder` | Placeholder not found in test body |
| `missing-literal` | String/numeric literal not found in test body |
| `example-mismatch` | Examples row has no matching `@example()` (or vice versa) |

## Architecture

```
beehave/
├── cli.py        argparse entry point
├── config.py     pyproject.toml loading
├── models.py     ScenarioInfo, TestInfo, Violation dataclasses
├── gherkin.py    .feature parsing via gherkin-official
├── discover.py   AST-based test file discovery
├── check.py      Dict-join consistency enforcement
├── generate.py   Stub generation with strategy inference
└── clean.py      Orphan removal
```

~1,250 lines of production code. No runtime framework. No cache. No state.

## License

MIT
