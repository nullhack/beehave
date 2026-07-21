# Glossary: beehave

> The ubiquitous language for this project — terms shared across conversation,
> code, and documentation (Evans, 2003). Curated for the IMPORTANT domain
> concepts, not every code symbol. Grouped by bounded context, where each term
> has one meaning. The tests are the source of truth for behaviour; this
> glossary is the source of truth for names.

## Context: Design-time (the CLI tool)

### `.feature`
A source artifact that holds Gherkin-syntax feature definitions and is the single source of truth for generation + check.
*Aliases: feature file*

### Feature
A Gherkin structural element that is the top-level container in a `.feature` file.
*Aliases: none*

### Rule
A Gherkin structural element that groups scenarios within a Feature and is the unit of per-rule test-file generation (`<feature_slug>_<rule_slug>_test.py`).
*Aliases: none*

### Background
A Gherkin structural element whose steps are merged into every scenario's step list and may not contain placeholders.
*Aliases: none*

### Scenario
A Gherkin structural element that maps one-to-one to a generated `test_<slug>` function whose name is its identity.
*Aliases: none*

### Scenario Outline
A Scenario parameterised by an Examples table; emitted with `@pytest.mark.parametrize` over the test function (one row per Examples row, all params typed `str`).
*Aliases: none*

### Examples
A tabular value source whose columns become `@parametrize` arg-names and whose rows become string-tuple parametrize rows. Multiple Examples tables in one Scenario Outline are merged; per-row tags tracked.
*Aliases: Examples table*

### step
A Gherkin structural element that is the unit matched one-to-one (`step[i]` at position N) against `with step(...)` blocks in the test body when Mode B runtime is active.
*Aliases: Gherkin step*

### placeholder
A parameterisation token of the form `<name>` that binds Examples-table columns to step-text positions and becomes a Python function parameter (typed `str`). Only recognised in Scenario Outline steps whose name appears in the Examples headers; `<foo>` in a plain Scenario or non-header position is literal text.
*Aliases: none*

### title
An identifier that derives the `test_<slug>` function name and is constrained by uniqueness (case-insensitive, slug-keyed), a 2–6 word-count bound, and a Unicode-letters/digits/spaces charset.
*Aliases: none*

### slug
A normalised identifier that is the lowercased, whitespace-collapsed form of a title. Slugs are the uniqueness key (titles differing only in whitespace runs collide) and the suffix of the `test_<slug>` function name + module filename.
*Aliases: none*

### Full Gherkin
A grammar-coverage claim meaning beehave parses everything `gherkin-official` emits, including `@tags`, docstrings, and data-tables. Tags surface as `pytestmark` / `@pytest.mark.<tag>`; docstrings and data-tables surface as body-local variables.
*Aliases: none*

### noise loophole
A spec-value-fidelity failure in which a placeholder or literal "appears" in a test body as an AST node while testing nothing about the step's actual behaviour — the v1 incident that motivates the v2 rewrite. Closed in v2 by removing appearance enforcement, and again in v3 by making `check` signature-only (body content is the consumer's responsibility).
*Aliases: none*

### `generate`
A CLI command that emits the `*_test.py` skeleton into `tests/features/` only if the file is absent (idempotent — never clobbers consumer bodies). One `<feature_slug>_default_test.py` for non-Rule scenarios + one `<feature_slug>_<rule_slug>_test.py` per Rule.
*Aliases: none*

### `check`
A CLI command that verifies the `.feature` ↔ `.py` contract 1-1: every scenario's expected `def test_<slug>(params) -> None` line must exactly equal some non-private top-level function signature in the corresponding `.py` module(s), and vice versa. Private `_*` functions are exempt (superset). Full sweep also runs orphan-module detection by filename stem; scoped invocation (`check <path>...`) skips it.
*Aliases: none*

### `status`
A CLI command that prints the `.feature` count under `docs/features/` and the `*_test.py` count under `tests/features/`; exit 0 if features dir exists, 2 if missing.
*Aliases: none*

### superset model
The v3.0.0 contract model: `.feature` is the sole source of truth; the `.py` non-private function surface must match it 1-1; private `_*` functions are an unconstrained superset (consumer helpers, fixture wrappers, etc.). Replaces v2's `.pyi`-driven stubtest gate.
*Aliases: none*

### orphan module
A `*_test.py` file in `tests/features/` whose stem does not correspond to any feature's expected module stems (derived from feature + rule slugs). Detected on full-sweep `beehave check`; reported to stderr; exit 1.
*Aliases: none*

### scoped check
`beehave check <path>...` — verifies only the named `.feature` paths. Skips orphan-module detection (which would require parsing every feature). Consumers wire incremental scope via git-diff.
*Aliases: none*

### parse model
The in-memory typed shapes (`Feature` / `Rule` / `Scenario` / `Step` / `Placeholder` / `Examples` / `Background` / `DataTable`) carried by `beehave/gherkin.py` as the shared vocabulary between `generate` and `check`. Distinguished from *persistence model* — beehave has none.
*Aliases: none*

### default group
The emission group for scenarios NOT under a Rule; emitted to `<feature_slug>_default_test.py` alongside one `<feature_slug>_<rule_slug>_test.py` per Rule.
*Aliases: none*

### skeleton
The `*_test.py` body emitted by `beehave generate` ONLY IF the `.py` is absent; a scaffold of `with step(...)` blocks (with `@parametrize` for Outlines, `pytestmark` for tags) the consumer fills. Re-running `generate` never clobbers an existing skeleton (idempotent).
*Aliases: test skeleton*

## Context: Runtime (beehave-the-import)

### Mode A — signature-only
The default usage mode: the consumer's `.py` non-private function signatures match the feature-derived signatures 1-1 (enforced by `beehave check`). The `from beehave import step` import + `with step(...)` blocks may be present or removed; check does not inspect them.
*Aliases: none*

### Mode B — step-enforced
The opt-in runtime mode: the consumer keeps the generated `with step(...)` blocks. At pytest time each block verifies against the scenario's step N (`keyword.lower()`, `text`, placeholder-name-set) and the `@parametrize` rows verify against `Examples`. Mismatches raise `StepError`; failures attribute via `add_note`.
*Aliases: none*

### `step`
A context manager imported `from beehave import step` that wraps a step's executable test code as `with step(keyword, text, **placeholders)`. Looks up the calling `test_*` frame, finds the scenario in the lazy index, advances a frame-keyed step counter, verifies the step N triple, and on exception attributes via `add_note(f"{keyword} {text}")`.
*Aliases: step context manager*

### keyword
A positional-only argument to the `step` context manager that is a STRING (data, not a method name) so it covers all Gherkin step keywords including localized variants without reserved-word clashes.
*Aliases: none*

### `Then`-asserts
A runtime contract that the `Then` step block is where the outcome assertion executes — the step block RUNS code, it does not merely declare it.
*Aliases: none*

### `add_note`
A PEP 678 mechanism that the `step` context manager uses to attribute a failure to its specific step by name (`f"{keyword} {text}"`), preserving the original traceback.
*Aliases: none*

### `StepError`
The exception raised by the `step` CM at runtime when a `with step(...)` block's `(keyword, text, placeholder-name-set)` triple does not match the feature scenario's step N — Mode B runtime enforcement.
*Aliases: none*

### `NoActiveScenarioError`
The exception raised by `beehave._index.get(function_name)` when the calling function name does not match any scenario in any feature under `docs/features/` — strict Mode B invariant.
*Aliases: none*

### scenario index
The lazy module-level `dict[function_name, Scenario]` in `beehave/_index.py`, built once per process on first `step(...)` call by scanning `Path.cwd()/docs/features/*.feature`. Subsequent lookups are O(1); `_reset()` is the test hook.
*Aliases: _index*

## Context: Typing contract

### `.pyi`
A type-stub file shipped with the **beehave package** (`beehave/*.pyi`) for consumer-side type-checkers. Consumer tests in `tests/features/` do NOT have `.pyi` siblings in v3.0.0 (dropped — the superset model derives the contract directly from `.feature`).
*Aliases: stub*

### `py.typed`
A PEP 561 package-marker file (empty) that signals to type-checkers that the beehave package ships typed stubs.
*Aliases: none*

### `mypy.stubtest`
A dev-only tool that verifies `.py` ↔ `.pyi` drift for the **beehave package itself** (`task stubtest` runs `python -m mypy.stubtest beehave --allowlist .stubtest_allowlist`). NOT used on consumer tests in v3.0.0.
*Aliases: stubtest*

### `.stubtest_allowlist`
A repo-root file listing stubtest false positives (regex matched against object paths). Carries one entry `beehave.step.step` (mypy `@contextmanager` positional-only param-name erasure false positive).
*Aliases: none*
