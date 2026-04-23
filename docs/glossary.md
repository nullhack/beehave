# Glossary: beehave

> Living glossary of domain terms used in this project.
> Written and maintained by the product-owner during Step 1 discovery.
> Append-only: never edit or remove past entries. If a term changes, mark it retired in favour of the new entry and write a new entry.
> Code and tests take precedence over this glossary — if they diverge, refactor the code, not this file.

---

## Entry Format

```
## <Term>

**Definition:** <one sentence — genus + differentia: "A [category] that [distinguishes it from others in that category]">

**Aliases:** <deprecated synonyms the team should stop using, or "none">

**Example:** <one sentence showing the term in use in this project; optional but encouraged>

**Source:** <feature stem or discovery session date>
```

Entries are sorted alphabetically.

---

## @id Tag

**Definition:** An 8-character lowercase hex identifier (e.g. `@id:a1b2c3d4`) attached to each Gherkin `Example:` block that uniquely links it to its corresponding test stub function.

**Aliases:** id tag, example id, test id

**Example:** "When beehave reads `@id:f0e1d2c3` on an Example, it looks for a test function named `test_login_f0e1d2c3` in the generated stubs."

**Source:** 2026-04-21 — Session 1; feature `id-generation`

---

## @deprecated Tag

**Definition:** A Gherkin tag that marks a Feature, Rule, or Example as retired, causing beehave to propagate a framework-specific deprecated marker onto the corresponding test stub.

**Aliases:** deprecated tag, deprecation marker

**Example:** "Adding `@deprecated` to a Rule cascades it to all Examples beneath — every corresponding test stub receives `@pytest.mark.deprecated`."

**Source:** 2026-04-21 — Session 1 (Supplement); feature `deprecation-sync`

---

## Acceptance Criteria

**Definition:** A set of conditions that a feature must satisfy before the product-owner considers it complete, expressed as Gherkin `Example:` blocks with `@id` tags.

**Aliases:** exit criteria

**Example:** "The `nest` feature's acceptance criteria specify that running `beehave nest` creates the directory structure and injects the config snippet."

**Source:** 2026-04-21 — Session 1; BDD practice

---

## Adapter

**Definition:** A pluggable module that translates beehave's framework-agnostic stub generation into the conventions and marker syntax of a specific test framework.

**Aliases:** framework adapter, test framework adapter

**Example:** "The pytest adapter supplies `@pytest.mark.skip(reason='not yet implemented')` as the skip marker template; the unittest adapter would supply a different pattern."

**Source:** 2026-04-21 — Session 1 (Q9, AC1–AC3); feature `adapter-contract`

---

## BDD (Behaviour-Driven Development)

**Definition:** A collaborative software development practice in which acceptance criteria are written as concrete examples of system behaviour, expressed in a structured natural language understood by both stakeholders and developers.

**Aliases:** Behaviour-Driven Development, Behavior-Driven Development (US spelling)

**Example:** "Beehave implements BDD by keeping Gherkin `.feature` files as the source of truth and auto-generating test stubs that reflect them."

**Source:** 2026-04-21 — Session 1; North (2006) BDD origin paper

---

## Cache

**Definition:** A JSON file at `.beehave_cache/features.json` that stores the last-known state of feature files and their stubs, enabling incremental sync instead of full re-generation.

**Aliases:** sync cache, feature cache

**Example:** "When `beehave sync` runs, it compares the current `.feature` files against the cache to determine which stubs need creating, updating, or flagging as orphaned."

**Source:** 2026-04-21 — Session 1 (CA1–CA2); feature `cache-management`

---

## Feature (Gherkin)

**Definition:** A unit of user-visible functionality described by a `.feature` file containing a title, narrative, rules, and acceptance criteria examples, serving as the single source of truth for test stub generation.

**Aliases:** feature file

**Example:** "The `login.feature` file defines all the expected login behaviours; beehave generates stubs that mirror its structure."

**Source:** 2026-04-21 — Session 1

---

## Feature Stage

**Definition:** A subdirectory under `docs/features/` — `backlog/`, `in-progress/`, or `completed/` — that indicates a feature's workflow status, with no behavioral difference in how beehave processes them.

**Aliases:** stage, workflow stage

**Example:** "A `.feature` file in `backlog/` generates the same stubs as one in `completed/`; the stage is a project management concern, not a beehave concern."

**Source:** 2026-04-21 — Session 1 (C10)

---

## Gherkin

**Definition:** A structured plain-English syntax for writing acceptance criteria using `Feature`, `Rule`, `Example`, `Given`, `When`, and `Then` keywords.

**Aliases:** Cucumber syntax, BDD syntax

**Example:** "`Given the project is nested`, `When the user runs beehave sync`, `Then stubs are generated for all unstubbed Examples` is a Gherkin example."

**Source:** 2026-04-21 — Session 1; Cucumber project

---

## Hatch

**Definition:** The `beehave hatch` CLI command that generates one or two bee-themed demo `.feature` files covering common Gherkin patterns, enabling an end-to-end sync workflow demonstration.

**Aliases:** demo generation, example generation

**Example:** "Running `beehave hatch` in a newly nested project creates a bee-themed `.feature` file with a Feature, Rule, Example, and Scenario Outline."

**Source:** 2026-04-21 — Session 1 (Q8, Supplement); feature `hatch`

---

## Nest

**Definition:** The `beehave nest` CLI command that bootstraps the canonical directory structure (`docs/features/{backlog,in-progress,completed}/`, `tests/features/`) and injects a `[tool.beehave]` snippet into `pyproject.toml`.

**Aliases:** bootstrap, init, project setup

**Example:** "Running `beehave nest` on a new project creates all required directories with `.gitkeep` files and adds the beehave config section to `pyproject.toml`."

**Source:** 2026-04-21 — Session 1 (N1–N11); feature `nest`

---

## Orphan

**Definition:** A test stub function whose `@id` in its name has no matching `@id` in any `.feature` file, indicating the feature example it was generated from has been removed.

**Aliases:** orphaned stub, orphaned test

**Example:** "After a `.feature` file is deleted, `beehave sync` warns about the orphaned stubs but does not delete them — the developer decides."

**Source:** 2026-04-21 — Session 1 (SCL1–SCL2); feature `sync-cleanup`

---

## Pyproject Config

**Definition:** The `[tool.beehave]` section in `pyproject.toml` that stores beehave's configuration, including framework selection, features directory path, template directory, and deletion handling behavior.

**Aliases:** beehave config, tool config

**Example:** "Setting `framework = 'pytest'` in `[tool.beehave]` tells beehave to use the pytest adapter by default."

**Source:** 2026-04-21 — Session 1 (C3); feature `config-reading`

---

## Rule

**Definition:** A Gherkin keyword that groups related Examples within a Feature, each Rule corresponding to one generated test file.

**Aliases:** rule block

**Example:** "A `Rule: Login validation` block in `login.feature` generates `tests/features/login/login_validation_test.py`."

**Source:** 2026-04-21 — Session 1 (SC2); feature `sync-create`

---

## Scenario Outline

**Definition:** A Gherkin keyword that defines a parameterised example template with an `Examples:` table, which beehave renders as a framework-specific parametrised test stub.

**Aliases:** outline, parametrised scenario

**Example:** "A Scenario Outline with username/password columns generates `@pytest.mark.parametrize(...)` in the pytest adapter."

**Source:** 2026-04-21 — Session 1 (PH1–PH2); feature `parameter-handling`

---

## Status

**Definition:** The `beehave status` CLI command that performs a dry-run preview of what `beehave sync` would change, exiting 0 if in sync and 1 if changes are pending.

**Aliases:** dry-run, preview, sync check

**Example:** "Running `beehave status --json` in CI returns machine-readable output and a non-zero exit code when stubs are out of date."

**Source:** 2026-04-21 — Session 1 (S1); feature `status`

---

## Stub

**Definition:** A minimal test function generated by beehave for a Gherkin Example, containing a framework-specific skip marker, a docstring with the full Gherkin steps, and an Ellipsis body.

**Aliases:** test stub, generated test

**Example:** "A stub for `@id:a1b2c3d4` is named `test_login_a1b2c3d4`, marked `@pytest.mark.skip`, and contains the Given/When/Then steps as a docstring."

**Source:** 2026-04-21 — Session 1 (SC1); feature `sync-create`

---

## Sync

**Definition:** The `beehave sync` CLI command that generates new stubs, updates existing stubs, and reports orphaned stubs based on the current state of `.feature` files.

**Aliases:** sync command, beehave sync

**Example:** "Running `beehave sync` after editing a `.feature` file updates the docstring of the corresponding test stub without touching its body."

**Source:** 2026-04-21 — Session 1 (Q8); features `sync-create`, `sync-update`, `sync-cleanup`

---

## Template

**Definition:** A text template (built-in or user-supplied) that defines the structure and markers of a generated test stub for a specific framework.

**Aliases:** stub template, adapter template

**Example:** "The pytest adapter's built-in template produces `@pytest.mark.skip(reason='not yet implemented')`; a custom template folder can replace it entirely."

**Source:** 2026-04-21 — Session 1 (T1–T3); feature `template-customization`

---
