# Specification (current state)

> The living specification of this project's current state — what it is and
> where it is in its build. Regenerated each pipeline cycle by the refresh step
> from the truth: tests, pending marks, cassettes, migrations, and the
> glossary. Never hand-edited; hand-authoring creates a second source of truth
> that drifts. Tests are the source of truth for behaviour — this file is a
> derived view. When prose and a test disagree, the test wins.

## Snapshot

- **Project:** beehave
- **Version:** 3.0.0
- **Generated:** 2026-07-21
- **Suite:** green · **Tests:** 66 · **Pending:** 0
- **Purpose:** → see `README.md`

## Entry points & boundaries

**Entry points:**
- CLI: `beehave generate|check [feature...]|status` (console-script `beehave = beehave.cli:main`).
- Import: `from beehave import step` — the runtime context manager used inside consumer-authored `*_test.py` bodies (Mode B opt-in).

**Boundary:**
- *Internal (ours):* `beehave.__init__`, `beehave.step`, `beehave._index`, `beehave.gherkin`, `beehave.generate`, `beehave.check`, `beehave.status`, `beehave.cli` (8 modules; parse-model shapes live in `beehave.gherkin` per Q2-resolution — no separate `models.py`).
- *External (depends on):* `gherkin-official` (parser; Full Gherkin coverage); pytest (test runner, hosts the `step` CM and `@parametrize`); mypy (dev-only; library stubtest gate).

## Contract index

The derived map of what this system does. Each row points at the test (the
behavioural truth) and the source module. Intent is regenerator-authored from
the test body and self-corrects each cycle.

| Contract | Module | Test | Intent (one line) | Status |
|---|---|---|---|---|
| `step` (Mode B runtime) | `beehave.step` | `tests/integration/step_cm_test.py` | `step(keyword, text, /, **placeholders)` CM; walks frames to find calling `test_*` fn; verifies step N against feature scenario (keyword/text/placeholder-set); verifies `@parametrize` rows against `Examples`; attributes failures via `add_note`. | built |
| scenario index | `beehave._index` | (exercised via `step_cm_test.py`) | Lazy module-level `dict[function_name, Scenario]`; built once per process from `Path.cwd()/docs/features/*.feature`; `_reset()` test hook. | built |
| parse model + `parse_feature` | `beehave.gherkin` | `tests/integration/parsing_test.py`, `tests/integration/title_derivation_test.py` | Parse `.feature` into `Feature`/`Rule`/`Scenario`/`Step`/`Placeholder`/`Examples`/`Background`/`DataTable`; enforce title rules (case-insensitive slug-keyed uniqueness, 2–6 words, Unicode charset); reject placeholders in Background; merge multiple Examples tables (track per-row tags). | built |
| `generate` | `beehave.generate` | `tests/integration/idempotency_test.py`, `tests/integration/parametrize_test.py`, `tests/e2e/generate_test.py` | Emit `<feature_slug>_default_test.py` + one `<feature_slug>_<rule_slug>_test.py` per Rule into `tests/features/`; `.py` skeleton only if absent (idempotent); `@parametrize` for Examples (string rows, `str` params); tags → `pytestmark` + `@pytest.mark.<tag>`; docstrings/data-tables → body-local vars. | built |
| `check` | `beehave.check` | `tests/integration/roundtrip_test.py`, `tests/integration/parametrize_test.py`, `tests/e2e/check_test.py` | AST-based 1-1 superset: parse `.feature` → derive `def test_<slug>(params) -> None` lines; parse `.py` AST → collect non-private top-level function signatures; return True iff sets equal. Private `_*` fns exempt. | built |
| `status` | `beehave.status` | `tests/e2e/status_test.py` | Print `.feature` count under `<root>/docs/features/` and `*_test.py` count under `<root>/tests/features/`; exit 0 if dir exists, 2 if missing. | built |
| `main` (CLI dispatch) | `beehave.cli` | `tests/e2e/{check,generate,status}_test.py` | Dispatch `beehave generate|check|status`; `_check_all` accepts feature path args for scoped check (skips orphan detection); full sweep runs orphan-module detection by filename stem. | built |
| `__version__` + `step` re-export | `beehave.__init__` | (no test) | Single source of truth for `__version__ = "3.0.0"`; re-export `step`, `StepError`, `NoActiveScenarioError`. | built |

## Composition & data flow

How the contracts assemble into the e2e path, and the data that flows through
it. Entity names follow `docs/glossary.md`.

```
author → docs/features/<feature>.feature
       → parse_feature(source: str) -> Feature
       → generate(root: Path) -> None  writes  tests/features/<feature_slug>_default_test.py
                                       + one <feature_slug>_<rule_slug>_test.py per Rule
                                       (only if the .py is absent — idempotent)
       → consumer fills *_test.py bodies with assertions inside the with step(...) blocks
       → check(feature_text: str, py_text: str) -> bool  parses .feature for expected sigs,
                                                          parses .py AST for actual sigs,
                                                          returns True iff sets equal (1-1)
       → pytest runs the consumer's *_test.py; the step CM verifies each with-step against
         the scenario's step N at runtime and attributes AssertionError via add_note
       → status(root: Path) -> int  reports .feature count + *_test.py count
```

**Data flow:** `str` (.feature text) → `Feature` (parse model) → filesystem
write (`.py` skeleton-if-absent) → `bool` (check) / `int` (status, cli). No
persistence layer — the cycle is stateless file emission.

## Dependencies

**External services** — wire shapes live in the cassettes (the authoritative
external contract); this table points at them and never restates the shape.

| Service | Purpose | Protocol | Cassette | Env vars |
|---|---|---|---|---|
| `gherkin-official` | Parse Full Gherkin (`.feature` → typed tree) | in-process Python lib | N/A — explore pass-through; no HTTP | none |
| pytest | Test runner hosting the `step` CM + `@parametrize` inside consumer `*_test.py` | in-process Python lib | N/A | none |
| mypy + `mypy.stubtest` | Dev-side library stubtest gate (`beehave/*` package only; NOT consumer tests in v3.0.0) | dev CLI | N/A — out-of-package per L3 non-blocks | none |

**Persistence** — schema lives in the migrations (the migration IS the schema
spec); this table points at them and never restates the DDL.

| Entity | Store | Migration |
|---|---|---|
| (none) | N/A — beehave has no persistence layer (stateless file emission per data-model §1) | N/A |

## Status & last cycle

- **Built:** 8 modules · **Pending:** 0 — backlog: none
- **Suite:** 66 tests green (integration + e2e), zero pending markers.
- **Last cycle:** v3.0.0 — superset model rearchitecture. Dropped consumer-side `.pyi` emission + consumer-side stubtest gate. `check` rewritten as AST-based 1-1 superset verification (`.feature`-derived signatures == `.py` non-private function signatures, with private `_*` fns exempt). Orphan detection collapsed INTO check by filename-stem on full sweep. Added `beehave check <path>...` for scoped incremental checks. Dropped `mypy` runtime dep (back to dev-only). Version 3.0.0 (major bump — breaking).
- **Carry-forward (not blocking):**
  - `scripts/strip_docstrings.py` referenced by 3 skills but not yet authored.
  - Plan-review-gate misses (3 incidental-fixture issues in v2 cycles) — recommend systematic incidental-title audit + `pytester.run` smoke probe at author-test-stubs/simulate-contracts.
