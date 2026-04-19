<div align="center">
  <img src="docs/images/banner.svg" alt="pytest-beehave" width="860"/>

  <br><br>

  <p><strong>Keeps your Gherkin acceptance criteria and test stubs in sync — automatically, every time pytest runs.</strong></p>

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

## Installation

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
