<div align="center">
  <img src="docs/images/banner.svg" alt="pytest-beehave" width="860"/>

  <br><br>

  <p><strong>Keeps your Gherkin acceptance criteria and test stubs in sync — automatically, every time pytest runs.</strong></p>

  [![PyPI][pypi-shield]][pypi-url]
  [![Contributors][contributors-shield]][contributors-url]
  [![Forks][forks-shield]][forks-url]
  [![Stargazers][stars-shield]][stars-url]
  [![Issues][issues-shield]][issues-url]
  [![MIT License][license-shield]][license-url]
  [![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen?style=for-the-badge)](https://nullhack.github.io/pytest-beehave/coverage/)
  [![CI](https://img.shields.io/github/actions/workflow/status/nullhack/pytest-beehave/ci.yml?style=for-the-badge&label=CI)](https://github.com/nullhack/pytest-beehave/actions/workflows/ci.yml)
  [![Python](https://img.shields.io/badge/python-3.13-blue?style=for-the-badge)](https://www.python.org/downloads/)
</div>

---

## What it does

pytest-beehave is a pytest plugin. Every time you run `pytest`, it reads your Gherkin `.feature` files and makes sure the corresponding test stub files are current:

- **No stub for a new `Example:`?** It creates one — a typed, skipped test function with the Given/When/Then steps as its docstring.
- **Steps changed in the feature file?** It updates the docstring. Your test body is never touched.
- **`Example:` missing an `@id` tag?** It writes one back into the feature file in-place.
- **`@id` disappeared from the feature file?** It marks the test `skip(reason="orphan")` so nothing runs silently.
- **`@deprecated` tag on a feature or rule?** The `deprecated` pytest marker propagates down to every affected test.

All of this happens in `pytest_configure` — before pytest collects a single test.

---

## Why pytest-beehave?

BDD frameworks sold a compelling promise: human-readable specifications that live alongside your tests, kept honest by the test suite itself. The promise is real. The implementation is the problem. Every scenario explodes into a constellation of `@given`, `@when`, and `@then` step functions scattered across multiple files, wired together by fragile string matching. Refactor one step and you're hunting across the codebase. Add a new scenario and you're registering glue code. The ceremony grows with every feature, and the spec drifts from reality anyway — silently in unused step definitions, loudly in broken ones, always painfully. Plain pytest, on the other hand, is refreshingly direct. But there's no business-readable layer: acceptance criteria live in tickets or comments, never in code, and nothing machine-enforces that what the stakeholder approved is what the test exercises.

pytest-beehave is the middle ground. Write your acceptance criteria in plain Gherkin — business-readable, version-controlled, owned by the team. The plugin does the worker-bee work: generating test stubs, keeping docstrings in sync with your steps, assigning stable IDs, and flagging drift before it silently rots. You implement the test body however you like, in plain pytest, with no step files and no glue. The hive stays in order automatically — that tedious, thankless, essential synchronisation work is handled so you never have to think about it again.

---

## Installation

Available on [PyPI](https://pypi.org/project/pytest-beehave/):

```bash
pip install pytest-beehave
```

No `conftest.py` changes required. The plugin registers itself via pytest's entry-point system.

---

## Quick start

**1. Write a feature file with an untagged `Example:`:**

```gherkin
# docs/features/in-progress/checkout.feature
Feature: Checkout

  Rule: Tax calculation

    Example: VAT is applied at the correct rate
      Given a cart with items totalling £100
      When the buyer is in the UK
      Then the order total is £120
```

**2. Run pytest:**

```bash
pytest
```

**3. Two things just happened automatically:**

The feature file was updated with a stable ID:

```gherkin
    @id:a3f2b1c4
    Example: VAT is applied at the correct rate
```

And a test stub was created at `tests/features/checkout/tax_calculation_test.py`:

```python
import pytest

@pytest.mark.skip(reason="not yet implemented")
def test_checkout_a3f2b1c4() -> None:
    """
    Given: a cart with items totalling £100
    When: the buyer is in the UK
    Then: the order total is £120
    """
```

**4. Implement the test and ship.**

The stub is already in the right place with the right name. Fill in the body and remove the `skip`.

---

## See it in 2 minutes

No feature files yet? Generate a working example project in one command:

```
$ pytest --beehave-hatch

[beehave] HATCH backlog/forager-journey.feature
[beehave] HATCH in-progress/waggle-dance.feature
[beehave] HATCH completed/winter-preparation.feature
[beehave] hatch complete
```

Three bee-themed `.feature` files land under `docs/features/`, covering every Gherkin construct the plugin supports: `Background`, `Rule`, `Example`, `Scenario Outline` with an `Examples` table, data tables, untagged scenarios (to trigger auto-ID), and `@deprecated`.

The `in-progress/waggle-dance.feature` file looks like this:

```gherkin
# language: en
Feature: Waggle Dance Communication

  Background:
    Given the hive is in active foraging mode
    And the dance floor is clear of obstacles

  Rule: Direction encoding

    @id:hatch003
    Example: Scout encodes flower direction in waggle run angle
      Given a scout has located flowers 200 metres to the north-east
      When the scout performs the waggle dance
      Then the waggle run angle matches the sun-relative bearing to the flowers

  Rule: Distance encoding

    @id:hatch004
    Scenario Outline: Scout encodes distance via waggle run duration
      Given a scout has located flowers at <distance> metres
      When the scout performs the waggle dance
      Then the waggle run lasts approximately <duration> milliseconds

      Examples:
        | distance | duration |
        | 100      | 250      |
        | 500      | 875      |
        | 1000     | 1500     |

    @id:hatch005
    Example: Scout provides a data table of visited flower patches
      Given the scout returns from a multi-patch forage
      When the scout performs the waggle dance
      Then the flower patch register contains the following entries:
        | patch_id | species       | quality |
        | P-001    | Lavender      | 0.92    |
        | P-002    | Clover        | 0.85    |
        | P-003    | Sunflower     | 0.78    |
```

Now run pytest:

```
$ pytest

[beehave] CREATE tests/features/forager_journey/forager_readiness_test.py
[beehave] CREATE tests/features/forager_journey/nectar_quality_control_test.py
[beehave] CREATE tests/features/waggle_dance/direction_encoding_test.py
[beehave] CREATE tests/features/waggle_dance/distance_encoding_test.py
```

The untagged `Example:` in `forager-journey.feature` got an `@id` written back in-place. Every stub is already in the right file with the right name:

```python
# tests/features/waggle_dance/distance_encoding_test.py

import pytest


class TestDistanceEncoding:
    @pytest.mark.skip(reason="not yet implemented")
    def test_waggle_dance_hatch004() -> None:
        """
        Background:
        Given: the hive is in active foraging mode
        And: the dance floor is clear of obstacles
        Given: a scout has located flowers at <distance> metres
        When: the scout performs the waggle dance
        Then: the waggle run lasts approximately <duration> milliseconds
        """
        raise NotImplementedError

    @pytest.mark.skip(reason="not yet implemented")
    def test_waggle_dance_hatch005() -> None:
        """
        Background:
        Given: the hive is in active foraging mode
        And: the dance floor is clear of obstacles
        Given: the scout returns from a multi-patch forage
        When: the scout performs the waggle dance
        Then: the flower patch register contains the following entries:
          | patch_id | species   | quality |
          | P-001    | Lavender  | 0.92    |
          | P-002    | Clover    | 0.85    |
          | P-003    | Sunflower | 0.78    |
        """
        raise NotImplementedError
```

Remove the `skip`, implement the test body, run `pytest` again. The hive stays in sync from here on automatically.

---

## How it works

pytest-beehave hooks into `pytest_configure`, the earliest possible entry point. Every stub exists on disk before pytest begins collection.

```
pytest invoked
  └─ pytest_configure fires
       ├─ Bootstrap    — create docs/features/{backlog,in-progress,completed}/ if missing
       ├─ Assign IDs   — write @id tags to untagged Examples (or fail loudly in CI)
       └─ Sync stubs
            ├─ Create stubs for new Examples
            ├─ Update docstrings when steps change
            ├─ Rename functions when the feature slug changes
            ├─ Mark orphaned tests (criterion deleted from feature file)
            ├─ Redirect non-conforming tests to canonical locations
            └─ Propagate @deprecated markers from Gherkin tags
  └─ Collection begins — every stub is already present
  └─ Tests run
```

---

## File layout

Beehave expects — and will create — this structure:

```
docs/features/
  backlog/          ← criteria waiting to be built
  in-progress/      ← criteria actively being implemented
  completed/        ← shipped criteria (orphan detection only; no stub updates)

tests/features/
  <feature-name>/
    <rule-slug>_test.py   ← one file per Rule: block
```

Every test function name encodes its criterion:

```
test_<feature_slug>_<@id>
```

---

## Markers

pytest-beehave manages four markers. Your own markers (`slow`, `unit`, `integration`) are never touched.

| Marker | Meaning |
|---|---|
| `skip(reason="not yet implemented")` | Stub created, not yet implemented |
| `skip(reason="orphan: ...")` | The `@id` no longer exists in any feature file |
| `skip(reason="non-conforming: moved to ...")` | Test was in the wrong file; canonical stub created |
| `deprecated` | Criterion retired via `@deprecated` Gherkin tag |

---

## Configuration

```toml
# pyproject.toml
[tool.beehave]
features_path = "docs/features"   # default; omit if this matches your layout
```

If `features_path` is set but the directory does not exist, pytest-beehave exits immediately with a clear error.

---

## CI behaviour

On a read-only filesystem (CI), pytest-beehave skips all write operations and instead **fails the run** if it finds any `Example:` without an `@id` tag. This enforces that IDs are always committed — drift is caught at the PR gate, not after merge.

---

## Requirements

| | Version |
|---|---|
| Python | ≥ 3.13 |
| pytest | ≥ 6.0 |

Optional: install `pytest-beehave[html]` for acceptance-criteria columns in pytest-html reports.

```bash
pip install "pytest-beehave[html]"
```

---

## Contributing

```bash
git clone https://github.com/nullhack/pytest-beehave
cd pytest-beehave
uv sync --all-extras
uv run task test && uv run task lint && uv run task static-check
```

Bug reports and pull requests are welcome on [GitHub](https://github.com/nullhack/pytest-beehave/issues).

---

## License

MIT — see [LICENSE](LICENSE).

**Author:** eol ([@nullhack](https://github.com/nullhack)) · [Documentation](https://nullhack.github.io/pytest-beehave)

<!-- MARKDOWN LINKS & IMAGES -->
[pypi-shield]: https://img.shields.io/pypi/v/pytest-beehave?style=for-the-badge&color=orange
[pypi-url]: https://pypi.org/project/pytest-beehave/
[contributors-shield]: https://img.shields.io/github/contributors/nullhack/pytest-beehave.svg?style=for-the-badge
[contributors-url]: https://github.com/nullhack/pytest-beehave/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/nullhack/pytest-beehave.svg?style=for-the-badge
[forks-url]: https://github.com/nullhack/pytest-beehave/network/members
[stars-shield]: https://img.shields.io/github/stars/nullhack/pytest-beehave.svg?style=for-the-badge
[stars-url]: https://github.com/nullhack/pytest-beehave/stargazers
[issues-shield]: https://img.shields.io/github/issues/nullhack/pytest-beehave.svg?style=for-the-badge
[issues-url]: https://github.com/nullhack/pytest-beehave/issues
[license-shield]: https://img.shields.io/badge/license-MIT-green?style=for-the-badge
[license-url]: https://github.com/nullhack/pytest-beehave/blob/main/LICENSE
