# IN_20260510_adversarial_review — Adversarial Review & Resolved Decisions

> **Status:** COMPLETE
> **Interviewer:** PO
> **Participant(s):** Project Founder
> **Session type:** Adversarial review + decision resolution

---

## General

| ID | Question | Answer |
|----|----------|--------|
| Q1 | What is this session about? | Adversarial review of all five IN files to find contradictions, gaps, and ambiguities before development begins. Followed by resolution of identified issues. |
| Q2 | What was the most critical issue found? | Content-hash IDs break when scenario text changes. If `@id:a1b2c3d4` is derived from scenario text, fixing a typo in the .feature file changes the ID, orphaning the linked test. This contradicts the goal of stable @id links. |

## Resolved Decisions

| ID | Topic | Previous State | Resolution |
|----|-------|---------------|------------|
| R1 | ID generation | Content-hash, deterministic (IN_20260510_cli_commands Q5) | **Random, permanent.** IDs are generated once by `beehave sync` and never change. If a scenario has no @id, sync generates a random 8-character ID and writes it into the .feature file. Editing scenario text does NOT change the ID. Re-running sync only generates IDs for scenarios that don't have one. |
| R2 | @And/@But ordering at adoption level 1 | Ambiguous — how does beehave know whether @And continues @Given or @When without a .feature file? | **Resolved: decorator stack order is sufficient.** @And and @But inherit the step type from the most recent @Given/@When/@Then in the decorator stack. `@Given("...") @And("...") @When("...") @Then("...")` — the @And continues @Given, no ambiguity. Level 1 ordering validation works via decorator position. |
| R3 | @Example parameter format | Not specified — keyword vs positional | **Positional.** @Example takes positional arguments matching the placeholder order in the step text. `@Example(100, 30, 70)` maps values to `<placeholder>` names in declaration order. This matches Gherkin's Examples table (positional by column order). |
| R4 | Strategy auto-inference | Three-level with naming convention heuristics (priority 2: type hints from placeholder names) | **Two levels, no naming convention heuristics.** (1) Module-level variable — explicit, always wins. (2) Infer from @Example values — the type of the value determines the strategy (`100` → `st.integers()`, `"Alice"` → `st.text()`, `True` → `st.booleans()`). (3) Fallback: `st.integers()` (configurable to error instead). No naming convention dictionary. |
| R5 | Inline kwargs on @Given | Pending (D3 in collection_mechanics) | **Dropped.** All five decorators (@Given, @When, @Then, @And, @But) take only a step text string. No inline strategy kwargs. Strategy resolution is module-level variables → infer from @Example → `st.integers()` fallback. |
| R6 | Background support | Deferred (D5) | **Option B with fixture steps.** A `@Background` decorator references a fixture function that has its own @Given/@When/@Then decorators. The fixture function body runs as setup. Multiple scenarios can share the same @Background. All parameters (including background parameters) appear in the test function signature (Option A for parameter passing). |
| R7 | Multiple .feature files per directory | Deferred (D6) | **One .feature file per feature, one test directory per feature.** 1:1 mapping. If a feature grows too large, split it into separate features. Can be relaxed later if needed. |

## @Background Design Details

| ID | Question | Answer |
|----|----------|--------|
| Q3 | How does @Background work? | A background fixture is a regular decorated function with @Given/@When/@Then/@And/@But steps. The `@Background(fixture_name)` decorator on a test function references this fixture. At collection time, beehave prepends the fixture's step decorators to the test's step list for validation and report generation. At runtime, the fixture function body runs as setup. |
| Q4 | Does the background fixture run setup code? | **Yes.** The fixture function body executes as setup before the test. This is the "Given" setup — creating users, initializing state, etc. |
| Q5 | Can multiple scenarios share the same @Background? | **Yes.** Multiple test functions can reference the same background fixture. This is the primary use case — shared setup across scenarios in the same feature. |
| Q6 | How are background parameters passed? | **Option A: all parameters in the test signature.** If the background fixture uses `<initial>` and the test uses `<amount>` and `<remaining>`, the test function signature is `def test_something(initial, amount, remaining)`. The test signature is the complete list of all parameters from both the background and the scenario. This makes @Example mapping unambiguous and keeps Hypothesis integration straightforward. |
| Q7 | Example of @Background usage? | See code example below. |

### @Background Code Example

```python
# Background fixture: shared setup for all balance scenarios
initial = st.integers(min_value=0)

@Given("a user with balance <initial>")
@And("the user is authenticated")
def background_balance_accounting(initial):
    user = User(initial_balance=initial)
    return user

# Scenario 1: spending
amount = st.integers(min_value=0)
remaining = st.integers(min_value=0)

@Background(background_balance_accounting)
@When("the user spends <amount>")
@Then("the balance should equal <remaining>")
@Example(100, 30, 70)
def test_spending_reduces_balance_kx7m2p9q(initial, amount, remaining):
    user = background_balance_accounting(initial)
    user.spend(amount)
    assert user.balance == remaining

# Scenario 2: deposit
@Background(background_balance_accounting)
@When("the user deposits <amount>")
@Then("the balance should equal <remaining>")
@Example(100, 50, 150)
def test_deposit_increases_balance_m3n4o5p6(initial, amount, remaining):
    user = background_balance_accounting(initial)
    user.deposit(amount)
    assert user.balance == remaining
```

## Strategy Inference Priority (Final)

| Priority | Source | Example | Fallback |
|----------|--------|---------|----------|
| 1 (highest) | Module-level variable | `initial = st.integers(min_value=0)` | — |
| 2 | @Example value type | `@Example(100, "Alice", True)` → `st.integers()`, `st.text()`, `st.booleans()` | — |
| 3 (lowest) | Default | `st.integers()` | Configurable to error in `pyproject.toml` |

## @Example Positional Mapping

```python
# Step text: "a user with balance <initial> spends <amount>"

@Example(100, 30)           # initial=100, amount=30
@Example(0, 50)             # initial=0, amount=50

# @Example values map to <placeholder> names in declaration order
# (left-to-right as they appear in the step text)
```

---

## Corrections to Previous INs

### IN_20260510_cli_commands

- **Q5 (ID format)**: CHANGED from content-hash to random. IDs are generated once by `beehave sync` and are permanent. Editing scenario text does NOT change the ID. The content-hash approach was rejected because it breaks links when scenario text changes.

### IN_20260510_beehave_design

- **Q10 (strategy resolution)**: FINAL. Two levels: module-level variable → infer from @Example values. No inline kwargs on @Given. No naming convention heuristics. Fallback to `st.integers()` (configurable to error).
- **Q18 (three-level strategy resolution)**: REMOVED. Was "module-level, inline kwargs, auto-infer." Now simplified to "module-level, infer from @Example, st.integers() fallback."

### IN_20260510_collection_mechanics

- **D1 (ID generation format)**: RESOLVED. Random 8-character IDs, generated once, permanent.
- **D3 (inline strategy kwargs on @Given)**: RESOLVED. Dropped. All decorators take only a step text string.
- **D5 (Background support)**: RESOLVED. @Background decorator referencing a fixture function with proper step decorators. All parameters in test signature.
- **D6 (Multiple .feature files per directory)**: RESOLVED. One .feature per feature, 1:1 mapping.

---

## Remaining Open Items

| ID | Topic | Status |
|----|-------|--------|
| O1 | @Example positional mapping — how does the developer know which position maps to which placeholder? Need to define the order (declaration order in step text? alphabetical?) | Needs resolution |
| O2 | Strategy inference type mapping — which Python types map to which Hypothesis strategies? (`int` → `st.integers()`, `str` → `st.text()`, `bool` → `st.booleans()`, `float` → `st.floats()`, `datetime` → `st.datetimes()`, others?) | Needs resolution |
| O3 | How does beehave inject Hypothesis `@given` at collection time? The mechanism (pytest hook? function wrapping? decorator transformation?) | Needs resolution |
| O4 | D4 (vocabulary source for level 4) — what validates step text at adoption level 4? .feature text? Glossary? Both? | Deferred |
| O5 | `beehave fix` adding missing function parameters to existing signatures — AST manipulation scope and safety | Needs resolution |
| O6 | `pyproject.toml` schema for beehave configuration (feature_paths, strict, max_examples, infer_strategies) | Needs resolution |

---

## Quality Attributes

| ID | Attribute | Scenario | Target | Priority |
|----|-----------|----------|--------|----------|
| QA1 | Stability | When a developer edits scenario text in a .feature file, the @id tag must not change | IDs are random and permanent once generated; only new scenarios get new IDs | Must |
| QA2 | Explicitness | When a developer reads a test function signature, they can see all parameters including those from background fixtures | All parameters appear in the test function signature; no hidden parameter injection | Must |
| QA3 | Simplicity | When a developer uses @Example, the mapping from values to placeholders must be unambiguous | Positional mapping follows placeholder declaration order in step text | Must |

---

## Pain Points Identified

- Content-hash IDs create fragile links — editing scenario text would orphan linked tests, defeating the purpose of stable traceability
- Naming convention heuristics for strategy inference create an implicit dictionary that developers must learn and maintain — rejected in favor of explicit resolution
- Background fixtures need to pass parameters to tests — hiding parameters makes @Example mapping ambiguous, so all parameters must be in the test signature

## Business Goals Identified

- Stable traceability — @id links must survive scenario text edits
- Explicit over implicit — strategy resolution, parameter passing, and @Example mapping should be visible in the test code
- Keep the API surface minimal — five decorators take only step text strings; no inline kwargs, no naming convention dictionaries

## Terms to Define (for glossary)

- **Random permanent ID** — An 8-character randomly generated ID assigned once by `beehave sync` and never changed. Editing scenario text does not affect the ID. Re-running sync only generates IDs for scenarios that don't have one.
- **@Background** — A decorator that references a background fixture function. The fixture provides shared setup (Given steps) and its parameters are merged into the test function's parameter list. Multiple scenarios can share the same @Background.
- **Positional @Example** — @Example takes positional arguments that map to `<placeholder>` names in the order they appear in step text.
- **Strategy inference from @Example** — When no module-level strategy variable exists for a placeholder, beehave infers the strategy from the type of the @Example value (int → st.integers(), str → st.text(), bool → st.booleans()).

## Action Items

- [ ] Update IN_20260510_cli_commands Q5 to reflect random permanent IDs (not content-hash)
- [ ] Update IN_20260510_beehave_design Q10 and Q18 to reflect final strategy resolution (two levels, no inline kwargs, no naming conventions)
- [ ] Update IN_20260510_collection_mechanics to mark D1, D3, D5, D6 as resolved
- [ ] Define @Example positional mapping order (declaration order in step text)
- [ ] Define strategy inference type mapping table
- [ ] Design the mechanism for beehave to inject Hypothesis @given at collection time
- [ ] Define the `pyproject.toml` schema