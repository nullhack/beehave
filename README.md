<div align="center">
  <img src="docs/images/banner.svg" alt="Beehave" width="860"/>

  <br><br>

  <p><strong>Your acceptance criteria and your test stubs — always in sync. Every time you run pytest.</strong></p>

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

## The drift problem

A healthy hive is one where every bee knows its role. A healthy codebase is one where every test knows its criterion.

In practice: you write a Gherkin `Example:`. You write a test stub. Three weeks later you rename the feature. The stub is stale. The docstring is wrong. The `@id` is missing from CI. And you find out at the worst possible moment.

Living documentation is supposed to keep specs and code in sync. In practice, that sync is always manual — and always falls behind.

**Beehave is the colony's memory.** A pytest plugin that tends your test stubs the way a hive tends its cells: precisely, automatically, and before any other work begins. Every time you invoke `pytest`, the colony is in order.

---

## What the colony does

| Capability | How Beehave tends the hive |
|---|---|
| **Stub generation** | New `@id`-tagged `Example:` → a typed, skipped test stub is built before collection runs |
| **Docstring sync** | Steps change in your `.feature`? Docstrings are resealed to match. Test bodies are never touched. |
| **Auto ID assignment** | Missing `@id` on an `Example:`? Beehave generates one and writes it back in-place — like a worker bee capping an open cell |
| **CI enforcement** | Read-only filesystem (CI)? Beehave fails loudly and names every untagged Example — no silent drift escapes the hive |
| **Orphan detection** | `@id` disappears from the feature file? The test is marked `skip(reason="orphan")` — preserved, not deleted, not silently executed |
| **Non-conforming redirect** | Test in the wrong file or class? Beehave builds the canonical stub in the correct cell and marks the original as relocated |
| **Deprecation sync** | `@deprecated` tag on an `Example:`, `Rule:`, or `Feature:`? The pytest marker propagates — inheritance flows down the comb |
| **Bootstrap** | No `docs/features/` yet? Beehave creates the canonical subfolder structure and migrates any loose `.feature` files into the right cells |
| **Zero config** | Works out of the box. Optionally configure `features_path` in `pyproject.toml` |

---

## Installation

```bash
pip install pytest-beehave
```

The plugin registers itself via pytest's entry-point system — no `conftest.py` changes needed. The hive is self-organizing.

---

## Quick start

**1. Write a feature file:**

```gherkin
# docs/features/in-progress/checkout.feature
Feature: Checkout

  Rule: Tax calculation
    As a buyer
    I want the correct tax applied to my order
    So that I pay the right amount

    Example: VAT is applied at the correct rate
      Given a cart with items totalling £100
      When the buyer is in the UK
      Then the order total is £120
```

**2. Run pytest:**

```bash
pytest
```

**3. Beehave has already built the cell:**

```python
# tests/features/checkout/tax_calculation_test.py

class TestTaxCalculation:
    @pytest.mark.skip(reason="not yet implemented")
    def test_checkout_a3f2b1c4(self) -> None:
        """
        Given: a cart with items totalling £100
        When: the buyer is in the UK
        Then: the order total is £120
        """
        raise NotImplementedError
```

The `@id` tag was also written back into your `.feature` file automatically — the cell is capped.

**4. Fill the cell with real implementation and ship.**

---

## The waggle dance — how it works

Beehave hooks into `pytest_configure`, the earliest possible hook. By the time pytest begins collecting tests, every stub already exists on disk. The same `pytest` invocation that encounters a new criterion also generates its stub.

```
pytest invoked
  └─ pytest_configure fires  ← Beehave enters here, before any test is seen
       ├─ Bootstrap: ensure docs/features/{backlog,in-progress,completed}/ exist
       ├─ Assign IDs: write @id tags to untagged Examples (or fail loudly in CI)
       ├─ Sync stubs:
       │    ├─ Create missing stubs for new Examples
       │    ├─ Update outdated docstrings to match current steps
       │    ├─ Rename functions whose feature slug changed
       │    ├─ Mark orphaned tests (no matching @id anywhere)
       │    ├─ Redirect non-conforming tests to canonical locations
       │    └─ Propagate @deprecated markers from Feature/Rule/Example
       └─ Hands control back to pytest
  └─ Collection begins — every stub is already present
  └─ Tests run
```

The colony always knows where to find the honey.

---

## Configuration

```toml
# pyproject.toml
[tool.beehave]
features_path = "docs/features"   # default — omit if this is your layout
```

If `features_path` is set but the directory does not exist, Beehave exits immediately with a clear error naming the missing path. A hive without a location is not a hive.

---

## The comb structure

Beehave expects (and will create) this feature directory layout:

```
docs/features/
  backlog/        ← criteria waiting to be built
  in-progress/    ← criteria actively being implemented
  completed/      ← shipped criteria (orphan detection only; no stub updates)
```

Test files follow the hexagonal grid — uniform, predictable, traceable:

```
tests/
  features/
    <feature-name>/
      <rule-slug>_test.py     ← one file per Rule: block
      examples_test.py        ← when the feature has no Rule: blocks
```

Every test function name encodes its criterion:

```
test_<feature_slug>_<8char_hex>
```

No fragile name matching. No guessing. Every stub traces back to its exact `Example:` by ID — like a cell number in the comb.

---

## Marker semantics

Beehave tends four markers. Your markers — `slow`, `unit`, `integration` — are never touched.

| Marker | Applied by | Meaning |
|---|---|---|
| `skip(reason="not yet implemented")` | Beehave | Cell built, not yet filled |
| `skip(reason="orphan: ...")` | Beehave | Cell's criterion no longer exists |
| `skip(reason="non-conforming: moved to ...")` | Beehave | Cell is in the wrong part of the comb |
| `deprecated` | Beehave | Criterion retired — marker inherited from `@deprecated` Gherkin tag |
| `slow` | You | Opt-in for Hypothesis and long-running tests |

---

## Compatibility

| Requirement | Version |
|---|---|
| Python | ≥ 3.13 |
| pytest | ≥ 6.0 |

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
