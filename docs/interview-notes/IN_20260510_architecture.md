# IN_20260510_architecture — Core Architecture: Decorator-Based Integration

> **Status:** COMPLETE
> **Interviewer:** PO
> **Participant(s):** Project Founder
> **Session type:** Architecture decision

---

## General

| ID | Question | Answer |
|----|----------|--------|
| Q1 | What is this session about? | Determining how beehave integrates with Hypothesis to apply `@given` and `@example` at runtime, and ensuring the core library is runner-agnostic (not tied to pytest). |
| Q2 | Why was this session needed? | An earlier proposal used a pytest hook (`pytest_collection_modifyitems`) to apply `@given` at collection time. The founder correctly identified that this ties the entire implementation to pytest, even though Hypothesis itself is runner-agnostic. The concern was not about pytest specifically, but about not coupling the core mechanism to any specific test runner. |
| Q3 | What was rejected? | Three approaches were rejected: (1) **Pytest hook only** — ties the core `@given` application to pytest, violating runner-agnosticism. (2) **Explicit `@scenario` wrapper** — adds redundant ceremony; the step decorators already identify a beehave test. (3) **Function factory** — destroys the decorator-based Gherkin style, too verbose. |

## Core Decision: @Given Applies @given At Import Time

| ID | Question | Answer |
|----|----------|--------|
| Q4 | How does beehave apply Hypothesis `@given` and `@example`? | **At import time, via standard Python decorator mechanics.** The `@Given` decorator is applied last (outermost in the stack). When it executes, it receives the function with all metadata already attached by `@Example`, `@Then`, `@When`, and `@And`/`@But`. At that point, `@Given` resolves strategies from module scope and applies `hypothesis.given(...)`, `hypothesis.settings(max_examples=1)`, and converts `@Example` metadata to `hypothesis.example()` calls. |
| Q5 | Why does this work at import time? | Python decorators stack bottom-to-top. `@Example(100, 30, 70)` is applied first (innermost), attaching metadata. Then `@Then`, `@When`, `@And`, `@But` attach their metadata. Finally `@Given` executes last, having access to all the metadata. It can then resolve strategies and apply Hypothesis decorators. |
| Q6 | What does the decorator stack look like? | ```python @Given("a user with balance <initial>")    # applied LAST — resolves strategies, applies @given @When("the user spends <amount>")           # attaches metadata @Then("the balance should equal <remaining>") # attaches metadata @Example(100, 30, 70)                        # attaches metadata def test_balance_kx7m2p9q(initial, amount, remaining):     ... ``` |
| Q7 | What does `@Given` do at import time? | (1) Collect all `<placeholder>` names from all step decorators (`@Given`, `@When`, `@Then`, `@And`, `@But`). (2) Resolve strategies from module scope — find variables matching placeholder names. (3) Apply `hypothesis.given(initial=initial, amount=amount, remaining=remaining)`. (4) Apply `hypothesis.settings(max_examples=1)` for Gherkin-decorated tests. (5) Convert `@Example` metadata to `hypothesis.example()` calls. (6) If `@Background` is present, merge background parameters and strategies. |
| Q8 | Is this runner-agnostic? | **Yes.** The core mechanism (decorators applying `@given` at import time) works with any test runner that can discover and execute Hypothesis tests. No pytest dependency for the core integration. |

## Architecture: Core vs. Integration

| ID | Question | Answer |
|----|----------|--------|
| Q9 | What is the core library responsible for? | (1) Step decorators (`@Given`, `@When`, `@Then`, `@And`, `@But`, `@Example`, `@Background`) that attach metadata and apply `@given`. (2) Strategy resolution from module scope and `@Example` type inference. (3) .feature file parser. (4) Step text validation and ordering validation. (5) CLI commands (sync, generate, fix, clean). (6) Failure report rendering (step text with placeholder values). |
| Q10 | What is the integration layer responsible for? | Runner-specific integration for collection-time validation and failure report output. This is where pytest hooks, unittest runners, or other test runners connect. **This session does not define the integration layer — it is deferred for further discussion.** |
| Q11 | What is the package structure? | `beehave/core/` contains the runner-agnostic library. `beehave/pytest_plugin.py` contains the pytest-specific integration. The core does not import pytest. The integration layer imports the core. |

## Strategy Resolution at Import Time

| ID | Question | Answer |
|----|----------|--------|
| Q12 | How are strategies resolved at import time? | `@Given` looks up module-level variables matching `<placeholder>` names. If `initial = st.integers(min_value=0)` exists in the module scope, `<initial>` resolves to that strategy. If no strategy is found, `@Given` falls back to inferring from `@Example` value types. If no `@Example` exists, falls back to `st.integers()`. |
| Q13 | What convention is required for strategy variables? | Strategy variables must be defined in module scope **before** the test function. If `initial = st.integers(min_value=0)` appears after the test function, resolution fails at import time because `@Given` executes when the module is imported. This is an accepted convention — module-level strategy variables are placed at the top of the file, similar to how imports and constants are organized. |
| Q14 | Is this convention acceptable? | Yes. Module-level strategy variables at the top of the file is a natural convention that mirrors how Python developers organize imports, constants, and test fixtures. It's also consistent with how Hypothesis strategies are typically defined. |

## Decorator Execution Order

| ID | Question | Answer |
|----|----------|--------|
| Q15 | What is the exact execution order of decorators? | Python applies decorators bottom-to-top (innermost first). For beehave, the execution order is: (1) `@Example(100, 30, 70)` — attaches `__beehave_examples__` metadata. (2) `@Then("the balance should equal <remaining>")` — attaches step metadata. (3) `@When("the user spends <amount>")` — attaches step metadata. (4) `@Given("a user with balance <initial>")` — collects all metadata, resolves strategies, applies `hypothesis.given()` and `hypothesis.settings()`, converts `@Example` to `hypothesis.example()`. The function returned by `@Given` is the Hypothesis-wrapped test. |
| Q16 | Does `@Background` affect the execution order? | `@Background` attaches metadata about which background fixture to use. `@Given` incorporates the background fixture's parameters and steps into strategy resolution and step collection. The background fixture itself is a regular decorated function that executes at import time independently. |

## What @Given Produces

| ID | Question | Answer |
|----|----------|--------|
| Q17 | What does the function look like after `@Given` processes it? | The returned function is a Hypothesis test with `@given`, `@settings`, and `@example` applied. It also retains `__beehave_steps__`, `__beehave_examples__`, and `__beehave_background__` attributes for use by the integration layer (reporting, validation). |
| Q18 | Can developers inspect what beehave did? | Yes. The function has `__beehave_steps__`, `__beehave_examples__`, `__beehave_background__`, `__beehave_given_applied__` (mapping of placeholder names to resolved strategies), and `__beehave_settings_applied__` attributes. This makes the "magic" inspectable and debuggable. |

---

## Quality Attributes

| ID | Attribute | Scenario | Target | Priority |
|----|-----------|----------|--------|----------|
| QA1 | Runner-agnosticism | When a developer uses beehave decorators, the core mechanism (strategy resolution, @given application) must work without pytest | The core library must not import pytest; @Given must apply @given at import time without any test runner dependency | Must |
| QA2 | Inspectability | When a developer inspects a beehave-decorated test function, they can see what strategies were resolved and what Hypothesis decorators were applied | The function must carry `__beehave_*__` attributes documenting resolved strategies, steps, and examples | Must |
| QA3 | Convention simplicity | When a developer defines strategy variables, they must be in module scope before the test function | Strategy variables at module top-level; this mirrors standard Python file organization | Must |

---

## Pain Points Identified

- Tying the core @given application to a pytest hook would couple beehave to a single test runner, violating Hypothesis's runner-agnostic design
- Strategy variables must be defined before the test function in the module — if placed after, import-time resolution fails. This is an accepted convention but needs documentation.

## Business Goals Identified

- Keep the core library runner-agnostic — the mechanism for applying @given must work with any test runner that can execute Hypothesis tests
- Use standard Python decorator mechanics — no function factories, no explicit wrapper decorators, no pytest hooks for core functionality
- Make the decorator stack self-documenting — reading the test code tells you everything about the scenario

## Terms to Define (for glossary)

- **Import-time application** — The mechanism by which `@Given` resolves strategies and applies Hypothesis decorators when the module is imported, not at collection time or runtime. This is standard Python decorator behavior.
- **Step metadata** — Attributes attached to the test function by step decorators (`__beehave_steps__`, `__beehave_examples__`, `__beehave_background__`). These are read by `@Given` at import time and by the integration layer at collection/reporting time.
- **Core library** — The runner-agnostic part of beehave: decorators, strategy resolution, .feature parser, validation, CLI commands, and reporting. Does not import pytest.
- **Integration layer** — The runner-specific part that connects beehave to a test runner (e.g., pytest plugin for collection-time validation and failure report output). Imports the core library.

## Updates to Previous INs

### IN_20260510_beehave_design

- **Q12** (step decorator runtime role): Updated — at import time, `@Given` collects step metadata and resolves strategies, then applies `hypothesis.given()` and `hypothesis.settings()`. At runtime on failure, step decorators serve as report templates rendering placeholder values into Gherkin-readable failure output.
- **Q15** (how step decorators compose with Hypothesis): Updated — `@Given` applies `@given` at import time, not via a pytest hook. The step decorators compose with Hypothesis through standard Python decorator mechanics.

### IN_20260510_adversarial_review

- **O3** (how does beehave inject Hypothesis @given): Resolved. `@Given` applies `@given` at import time via standard Python decorator mechanics. No pytest hook needed for core functionality.

## Deferred Items

| ID | Topic | Notes |
|----|-------|-------|
| D1 | Collection-time validation integration | How step text validation against .feature files hooks into the test runner. Needs further discussion — may be a pytest hook, may be a standalone check. |
| D2 | Failure report integration | How Gherkin-readable failure reports hook into the test runner's output. Needs further discussion — may be a pytest hook, may be a standalone reporter. |

## Action Items

- [ ] Investigate whether `@Given` can reliably resolve module-level strategy variables at import time (Python module import order, circular imports)
- [ ] Design the `__beehave_*__` metadata attributes schema
- [ ] Investigate `@Background` interaction with `@Given`'s strategy resolution (merging background and scenario parameters)
- [ ] Further discuss collection-time validation and failure report integration (runner-agnostic vs pytest-specific)
- [ ] Design the package structure (`beehave/core/` vs `beehave/pytest_plugin.py`)