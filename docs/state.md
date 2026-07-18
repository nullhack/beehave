# Specification (current state)

> The living specification of this project's current state — what it is and
> where it is in its build. Regenerated each pipeline cycle by the refresh step
> from the truth: test `.pyi`, pending marks, cassettes, migrations, and the
> glossary. Never hand-edited; hand-authoring creates a second source of truth
> that drifts. Tests are the source of truth for behaviour — this file is a
> derived view. When prose and a test disagree, the test wins.

## Snapshot

- **Project:** beehave
- **Version:** 2.0.0
- **Generated:** 2026-07-18 by flowr session `beehave-v2`
- **Suite:** green · **Contracts:** 7/7 built (0 pending)
- **Purpose:** → see `README.md`

## Entry points & boundaries

**Entry points:**
- CLI: `beehave generate|check|status` (console-script `beehave = beehave.cli:main`).
- Import: `from beehave import step` — the runtime context manager used inside consumer-authored `*_test.py` bodies.

**Boundary:**
- *Internal (ours):* `beehave.__init__`, `beehave.step`, `beehave.gherkin`, `beehave.generate`, `beehave.check`, `beehave.status`, `beehave.cli` (7 modules; parse-model shapes live in `beehave.gherkin` per Q2-resolution — no separate `models.py`).
- *External (depends on):* `gherkin-official` (parser; Full Gherkin coverage); Hypothesis (imported by generated `*_test.py`, NOT by the package); pytest (test runner, hosts the `step` CM); consumer-side mypy + `mypy.stubtest` (the gate — runs in consumer CI, not in-package). See Dependencies.

## Contract index

The derived map of what this system does. Each row points at the test (the
behavioural truth) and the source `.pyi` (the type surface). Intent is
regenerator-authored from the test body and self-corrects each cycle.

| Contract | Module | Test | Intent (one line) | Status |
|---|---|---|---|---|
| `step` | `beehave.step` | `tests/integration/step_cm_test.py` | `step(keyword, text, /, **placeholders)` CM runs the block, attributes failures via `add_note`, positional-only keyword/text. | built |
| parse model + `parse_feature` | `beehave.gherkin` | `tests/integration/parsing_test.py`, `tests/integration/title_derivation_test.py` | Parse `.feature` into `Feature`/`Rule`/`Scenario`/`Step`/`Placeholder`/`Examples`/`Background`/`DataTable`; enforce title rules (case-insensitive uniqueness, 2–6 words, charset) and reject placeholders in Background. | built |
| `generate` | `beehave.generate` | `tests/integration/idempotency_test.py`, `tests/integration/strategy_inference_test.py` | Emit `<feature>_default_test.py{i,}` + one `<feature>_<rule>_test.py{i,}` per Rule; `.pyi` always, `.py` skeleton only if absent; Examples-column → strategy inference (int/float/bool/str; no-Examples → str). | built |
| `check` | `beehave.check` | `tests/integration/roundtrip_test.py`, `tests/e2e/check_test.py` | Structural binding: `block[i]`↔`step[i]` on (keyword case-insensitive, text, placeholder-name-set); body-content NOT inspected (noise loophole closed). | built |
| `status` | `beehave.status` | `tests/e2e/status_test.py` | Print `.feature` count under `<root>/docs/features/` and `*_test.pyi` count under `<root>/tests/`; exit 0 if dir exists, 2 if missing. | built |
| `main` (CLI dispatch) | `beehave.cli` | `tests/e2e/{check,generate,status}_test.py` | Dispatch `beehave generate|check|status` and return each subcommand's exit code; `argv` defaults to `sys.argv[1:]`. | built |
| `__version__` + `step` re-export | `beehave.__init__` | (no test — Q10 deferral) | Single source of truth for `__version__ = "2.0.0"`; re-export `step` for `from beehave import step`. | built |

## Composition & data flow

How the contracts assemble into the e2e path, and the data that flows through
it. Entity names follow `docs/glossary.md`.

```
author → docs/features/<feature>.feature
       → parse_feature(source: str) -> Feature
       → generate(root: Path) -> None  writes  tests/<feature>_default_test.py{i,} + one <feature>_<rule>_test.py{i,} per Rule
       → consumer fills *_test.py bodies with `with step(keyword, text, **placeholders): ...`
       → check(feature_text: str, test_py_text: str) -> bool  walks with-step blocks in source order
       → pytest runs the consumer's *_test.py; the step CM attributes any AssertionError to its step via add_note
       → status(root: Path) -> int  reports .feature count + *_test.pyi count
       → consumer CI: mypy on beehave.* + mypy.stubtest (the gate — out of package)
```

**Data flow:** `str` (.feature text) → `Feature` (parse model) → filesystem write (`.pyi` always, `.py` skeleton-if-absent) → `bool` (check) / `int` (status, cli). No persistence layer — the cycle is stateless file emission (data-model §1).

## Dependencies

**External services** — wire shapes live in the cassettes (the authoritative
external contract); this table points at them and never restates the shape.

| Service | Purpose | Protocol | Cassette | Env vars |
|---|---|---|---|---|
| `gherkin-official` | Parse Full Gherkin (`.feature` → typed tree) | in-process Python lib | N/A — explore pass-through; no HTTP | none |
| Hypothesis | Property-based strategies (`@given`/`@example`) for generated tests | in-process Python lib (consumer-side) | N/A — imported by generated `*_test.py`, not by beehave | none |
| pytest | Test runner hosting the `step` CM inside consumer `*_test.py` | in-process Python lib | N/A | none |
| mypy + `mypy.stubtest` | Consumer-side type gate + `.py`↔`.pyi` drift detector | CLI (consumer CI) | N/A — out-of-package per L3 non-blocks | none |

**Persistence** — schema lives in the migrations (the migration IS the schema
spec); this table points at them and never restates the DDL.

| Entity | Store | Migration |
|---|---|---|
| (none) | N/A — beehave v2 has no persistence layer (stateless file emission per data-model §1) | N/A |

## Status & last cycle

- **Built:** 7 · **Pending:** 0 — backlog: none
- **Last cycle:** the beehave-v2 rewrite — 5 build cycles (`step`, `gherkin`, `generate`, `check`, `status`+`cli`) shipped green at `2.0.0`; 55 tests across integration (33) and e2e (22); 3 build-escalations resolved (`parsing_test` 1-word filler, `roundtrip_test` feature-vs-scenario collision, `tests/e2e` pytester-chdir path bug).
- **Next:** none — shipped. v3 spec exploration lives under `docs/spec/v3/` for a future cycle's discovery pass.
