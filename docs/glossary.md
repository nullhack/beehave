# Glossary: beehave

> The ubiquitous language for this project — terms shared across conversation,
> code, and documentation (Evans, 2003). Curated from the interview for the
> IMPORTANT domain concepts, not every code symbol. Grouped by bounded context,
> where each term has one meaning. The tests are the source of truth for
> behaviour; this glossary is the source of truth for names. Extend or revise
> entries as understanding shifts.

## Context: Design-time (the CLI tool)

### `.feature`
A source artifact that holds Gherkin-syntax feature definitions and is the single source of truth for generation.
*Aliases: feature file · Source: interview 2026-07-18*

### Feature
A Gherkin structural element that is the top-level container in a `.feature` file.
*Aliases: none · Source: interview 2026-07-18*

### Rule
A Gherkin structural element that groups scenarios within a Feature and is the unit of per-rule test-file generation.
*Aliases: none · Source: interview 2026-07-18*

### Background
A Gherkin structural element whose steps are merged into every scenario's step list and may not contain placeholders.
*Aliases: none · Source: interview 2026-07-18*

### Scenario
A Gherkin structural element that maps one-to-one to a generated `test_<slug>` function whose name is its identity.
*Aliases: none · Source: interview 2026-07-18*

### Examples
A tabular value source whose columns drive Hypothesis `@given` strategy inference and whose rows drive `@example`.
*Aliases: Examples table · Source: interview 2026-07-18*

### step
A Gherkin structural element that is the unit matched one-to-one (`block[i]`↔`step[i]`) against `with step(...)` blocks in the test body.
*Aliases: Gherkin step · Source: interview 2026-07-18*

### placeholder
A parameterisation token of the form `<name>` that binds Examples-table columns to step-text positions and whose name-set is one of the three structural-binding fields.
*Aliases: none · Source: interview 2026-07-18*

### title
An identifier that derives the `test_<slug>` function name and is constrained by uniqueness (case-insensitive), a 2–6 word-count bound, and a Unicode-letters/digits/spaces charset.
*Aliases: none · Source: interview 2026-07-18*

### slug
A normalised identifier that is the lowercased, whitespace-collapsed form of a title and becomes the suffix of the `test_<slug>` function name.
*Aliases: none · Source: interview 2026-07-18*

### Full Gherkin
A grammar-coverage claim meaning v2 parses everything `gherkin-official` emits, including `@tags`, docstrings, and data-tables.
*Aliases: none · Source: interview 2026-07-18*

### noise loophole
A spec-value-fidelity failure in which a placeholder or literal "appears" in a test body as an AST node while testing nothing about the step's actual behaviour — the v1 incident that motivates v2.
*Aliases: none · Source: interview 2026-07-18 (CIT)*

### `generate`
A CLI command that emits the `.pyi` typed-stub contract always and the `*_test.py` skeleton only if the `.py` is absent (idempotent — never clobbers existing bodies).
*Aliases: none · Source: interview 2026-07-18*

### `check`
A CLI command that validates the `with step(...)` structural binding against the `.feature` and enforces title rules.
*Aliases: none · Source: interview 2026-07-18*

### `status`
A CLI command that reports generation/check progress (detailed behaviour deferred to plan).
*Aliases: none · Source: interview 2026-07-18*

### parse model
The in-memory typed shapes (`Feature` / `Rule` / `Scenario` / `Step` / `Placeholder` / `Examples` / `Background` / `DataTable`) carried by `beehave/models.py` as the shared kernel between `gherkin.py`, `generate.py`, and `check.py`. Distinguished from *persistence model* — v2 has none (the parse model is the binding data contract).
*Aliases: none · Source: data-model 2026-07-18*

### shared kernel
A bounded-context pattern (Evans, 2003) applied to `beehave/models.py`: a small explicitly-shared vocabulary consumed by `gherkin.py`, `generate.py`, and `check.py`. The seam is justified by the three-consumer access pattern; whether it stays its own module or collapses into `gherkin.py` is an internal source-structure choice, not a data-model concern.
*Aliases: none · Source: interview 2026-07-18 (L3) + data-model 2026-07-18*

### structural binding
The `block[i]`↔`step[i]` match on exactly `(keyword, text, placeholder-name-set)` — with `keyword` compared case-insensitively — that `beehave check` enforces by walking the test body's `with step(...)` blocks in source order. Body fidelity is deferred to the review gate; this is the structural-only check that replaces v1's appearance enforcement (the noise loophole).
*Aliases: none · Source: interview 2026-07-18 (L1 Success) + plan design decision 2026-07-18 (keyword case)*

### default group
The emission group for scenarios NOT under a Rule; emitted to `<feature_slug>_default_test.py{i,}` alongside one `<feature_slug>_<rule_slug>_test.py{i,}` per Rule.
*Aliases: none · Source: plan design decision 2026-07-18*

### skeleton
The `*_test.py` body emitted by `beehave generate` ONLY IF the `.py` is absent; a scaffold of `with step(...)` blocks the consumer fills. Re-running `generate` never clobbers an existing skeleton (idempotent) — only the `.pyi` is rewritten.
*Aliases: test skeleton · Source: interview 2026-07-18 (Constraint 1)*

## Context: Runtime (beehave-the-import)

### `step`
A context manager imported `from beehave import step` that wraps a step's executable test code as `with step(keyword, text, **placeholders)` and attributes failures to its step via `add_note`.
*Aliases: step context manager · Source: interview 2026-07-18*

### keyword
A positional argument to the `step` context manager that is a STRING (data, not a method name) so it covers all Gherkin step keywords including localized variants without reserved-word clashes.
*Aliases: none · Source: interview 2026-07-18*

### `Then`-asserts
A runtime contract that the `Then` step block is where the outcome assertion executes — the step block RUNS code, it does not merely declare it.
*Aliases: none · Source: interview 2026-07-18*

### `add_note`
A pytest mechanism that the `step` context manager uses to attribute a failure to its specific step by name.
*Aliases: none · Source: interview 2026-07-18*

## Context: Typing contract

### `.pyi`
A type-stub file that is the typed contract surface `generate` always emits and that consumer type-checkers read in preference to the `.py`.
*Aliases: stub · Source: interview 2026-07-18*

### `py.typed`
A PEP 561 package-marker file (empty) that signals to type-checkers that the package ships typed stubs, on which the consumer-side mypy gate depends.
*Aliases: none · Source: interview 2026-07-18*

### drift
A contract violation in which a generated `*_test.py` body diverges from its `.pyi`.
*Aliases: stub drift · Source: interview 2026-07-18*

### `mypy.stubtest`
A tool that is the SOLE `.py`↔`.pyi` drift detector in v2's gate (pyright/mypy read only the `.pyi`).
*Aliases: stubtest · Source: interview 2026-07-18*
