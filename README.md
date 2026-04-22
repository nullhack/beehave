<div align="center">

<img src="docs/assets/banner.svg" alt="beehave" width="100%"/>

<br/><br/>

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen?style=for-the-badge)](https://nullhack.github.io/beehave/coverage/)
[![CI](https://img.shields.io/github/actions/workflow/status/nullhack/beehave/ci.yml?style=for-the-badge&label=CI)](https://github.com/nullhack/beehave/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.13-blue?style=for-the-badge)](https://www.python.org/downloads/)

**BDD living documentation in sync.**

</div>

> **Beta — coming soon.** `beehave` is under active development and not yet available on PyPI. APIs, CLI flags, and configuration keys may change before the stable release.

---

`beehave` is a framework-agnostic CLI and Python library that keeps your Gherkin `.feature` files and test stubs in sync. It reads `.feature` files as the single source of truth, assigns stable `@id` tags to untagged examples, and generates or updates test stub functions — without ever touching your test bodies.

---

## How it works

`.feature` files are your source of truth. `beehave` bridges them to your test suite:

1. **`beehave nest`** — bootstraps the canonical directory structure (`docs/features/`, `tests/features/`, `.gitkeep` files, `[tool.beehave]` config in `pyproject.toml`).
2. **`beehave sync`** — assigns `@id` tags to untagged Examples, then creates, updates, or cleans up test stub functions to match the current state of every `.feature` file.
3. **`beehave status`** — shows what `sync` would change, without modifying anything. Exits 0 if in sync, 1 if changes are pending.
4. **`beehave hatch`** — generates bee-themed demo `.feature` files to try the full sync workflow end-to-end.
5. **`beehave version`** — prints the current version.

---

## Framework adapters

`beehave` ships with a built-in **pytest adapter** (v1). Adapters supply the stub template style — skip marker, deprecated marker, parametrize syntax, function prefix, return type, and body. The core is adapter-agnostic; swapping the adapter changes the generated output without touching `beehave`'s logic.

```toml
# pyproject.toml
[tool.beehave]
framework = "pytest"   # default
```

**v1**: pytest adapter included.
**v2**: unittest adapter planned.

---

## Installation

```bash
pip install beehave            # core only (brings the pytest adapter)
pip install beehave[pytest]    # core + pytest-specific extras
```

---

## Quick start

```bash
# 1. Bootstrap the structure
beehave nest

# 2. Write or drop in a .feature file, then sync
beehave sync

# 3. See what would change before committing
beehave status
```

---

## Generated stub shape (pytest adapter)

```python
@pytest.mark.skip(reason="not yet implemented")
def test_login_a1b2c3d4() -> None:
    """
    Given a registered user
    When they submit valid credentials
    Then they are redirected to the dashboard
    """
    ...
```

- Function name: `test_<feature_slug>_<id>`
- One file per `Rule:` block: `tests/features/<feature_slug>/<rule_slug>_test.py`
- Docstring: full Gherkin step text verbatim
- Body: `...` — never overwritten by `beehave`

---

## What beehave never does

- Modifies test bodies
- Deletes test stubs silently (warns only)
- Changes anything in `.feature` files except adding `@id` tags to untagged Examples
- Runs your tests (that is your test runner's job)

---

## `pytest-beehave`

A separate project — `pytest-beehave` — wraps `beehave` as a pytest plugin, adding automatic sync during the pytest lifecycle, HTML acceptance criteria injection, and terminal criteria output. That project is out of scope here.

---

## Configuration

```toml
[tool.beehave]
framework = "pytest"          # adapter to use
features_dir = "docs/features"  # where .feature files live
template_path = ""            # custom template folder (overrides built-in)
```

---

## CLI flags

| Flag | Effect |
|---|---|
| `--framework <name>` | Override the adapter for this invocation |
| `--overwrite` | Recreate managed directories from scratch (`nest` only) |
| `--check` | Verify structure without modifying anything (`nest` only) |
| `--template-dir <path>` | Use a custom template folder |
| `--verbose` | Human-readable output |
| `--json` | Machine-readable output (CI-friendly) |

---

## Commands

```bash
uv run task test          # full suite + coverage
uv run task test-fast     # fast, no coverage (use during TDD loop)
uv run task lint          # ruff format + check
uv run task static-check  # pyright type checking
uv run task run           # run the CLI
uv run task doc-build     # build API docs + coverage report
```

---

## License

MIT — see [LICENSE](LICENSE).

**Author:** [@nullhack](https://github.com/nullhack) · [Documentation](https://nullhack.github.io/beehave)

<!-- MARKDOWN LINKS -->
[contributors-shield]: https://img.shields.io/github/contributors/nullhack/beehave.svg?style=for-the-badge
[contributors-url]: https://github.com/nullhack/beehave/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/nullhack/beehave.svg?style=for-the-badge
[forks-url]: https://github.com/nullhack/beehave/network/members
[stars-shield]: https://img.shields.io/github/stars/nullhack/beehave.svg?style=for-the-badge
[stars-url]: https://github.com/nullhack/beehave/stargazers
[issues-shield]: https://img.shields.io/github/issues/nullhack/beehave.svg?style=for-the-badge
[issues-url]: https://github.com/nullhack/beehave/issues
[license-shield]: https://img.shields.io/badge/license-MIT-green?style=for-the-badge
[license-url]: https://github.com/nullhack/beehave/blob/main/LICENSE
