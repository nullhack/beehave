# IN_20260510_settings_and_defaults — Hypothesis Settings & beehave Defaults

> **Status:** COMPLETE
> **Interviewer:** PO
> **Participant(s):** Project Founder
> **Session type:** Domain deep-dive

---

## General

| ID | Question | Answer |
|----|----------|--------|
| Q1 | What is this session about? | Determining how beehave controls Hypothesis's generation count for Gherkin-decorated tests, and establishing default behavior that balances thoroughness with development speed. |
| Q2 | Why is this important? | Hypothesis runs 100 examples by default per `@given` test. For a project with many Gherkin scenarios, this makes the test suite impractically slow during development. The founder's primary concern is catching implementations that are hardcoded around the tests — even one random example exposes this. |

## Default Generation Count

| ID | Question | Answer |
|----|----------|--------|
| Q3 | What is the default `max_examples` for beehave tests? | **1**. One randomly generated example is sufficient to catch the main issue: implementations hardcoded around specific test values. Combined with the explicit `@Example` rows, this provides deterministic coverage plus minimal random exploration. |
| Q4 | Does this default apply to all Hypothesis tests? | **No.** The `max_examples=1` default applies **only to Gherkin-decorated tests** (tests using @Given/@When/@Then/@And/@But decorators). Regular Hypothesis tests without beehave decorators use Hypothesis's own default (100) or whatever the developer configured. beehave must not interfere with non-Gherkin tests. |
| Q5 | Why 1 and not 0? | `max_examples=0` would disable generation entirely, meaning only explicit `@Example` rows run. That's useful as a mode (examples-only) but shouldn't be the default. The default should generate at least one random example to catch hardcoded implementations. |
| Q6 | Is this configurable? | Yes. Configurable in `pyproject.toml` under the beehave configuration section. Developers can increase `max_examples` for CI or decrease for rapid TDD cycles. |

## @Example vs @example

| ID | Question | Answer |
|----|----------|--------|
| Q7 | What is the naming convention for beehave's example decorator? | **`@Example`** (uppercase E). This distinguishes beehave's decorator from Hypothesis's `@example` (lowercase e). Both may coexist on a test function — `@Example` for Gherkin explicit examples, `@example` for Hypothesis-specific edge cases. |
| Q8 | Why uppercase E? | Consistency with beehave's capitalized Gherkin keywords: @Given, @When, @Then, @And, @But, @Example. Hypothesis's `@example` remains lowercase as a separate, parallel mechanism. This makes it immediately clear which decorator comes from which library. |
| Q9 | How does `@Example` relate to Hypothesis's `@example`? | They are **additive**, not overlapping. Hypothesis's execution model: `@example` rows run first in Phase.explicit, then `max_examples` generated examples run in Phase.generate. `@Example` rows from beehave are converted to Hypothesis `@example` decorators at collection time. A test with `@Example(initial=100)` and `max_examples=1` runs: the explicit example first, then 1 generated example. Total: 2 runs. |

## Execution Model

| ID | Question | Answer |
|----|----------|--------|
| Q10 | What is the total execution count for a beehave test? | `Total runs = @Example rows + max_examples`. With default `max_examples=1` and 2 `@Example` rows, the total is 3 runs: 2 explicit examples + 1 generated example. |
| Q11 | What happens when an @Example fails? | Fail-fast: Hypothesis stops immediately. No generation occurs. This is standard Hypothesis behavior — explicit examples are validated first, and if any fail, the test reports the failure without generating random inputs. |
| Q12 | What happens when a generated example fails? | Hypothesis shrinks the failing example to the minimal counterexample. The Gherkin failure report renders the minimal counterexample's values into the step text, producing a stakeholder-readable failure scenario. |

## Configuration

| ID | Question | Answer |
|----|----------|--------|
| Q13 | Where is beehave configuration stored? | `pyproject.toml` under a `[tool.beehave]` section. This is where `max_examples`, feature file paths, strict/permissive mode, and other beehave settings are configured. |
| Q14 | Can settings be overridden per-test? | Yes, via Hypothesis's standard `@settings(max_examples=N)` decorator on individual tests. beehave sets the default for Gherkin-decorated tests; developers can override for specific scenarios that need more exploration. This is not a beehave feature — it's just Hypothesis working as expected. |
| Q15 | Should Hypothesis settings go in .feature files? | **No.** Settings belong in Python configuration (`pyproject.toml` or `@settings`), not in stakeholder-facing Gherkin files. The `.feature` file is a specification document, not a test configuration file. Only `@id:` tags go in .feature files for now. |

## Examples-Only Mode

| ID | Question | Answer |
|----|----------|--------|
| Q16 | Is there a mode that skips generation entirely? | Not as a named mode, but setting `max_examples=0` in `pyproject.toml` effectively creates an examples-only mode where only `@Example` rows run. This is useful during active development when iterating on scenarios. This is just Hypothesis configuration — beehave doesn't need a special mode. |

---

## Quality Attributes

| ID | Attribute | Scenario | Target | Priority |
|----|-----------|----------|--------|----------|
| QA1 | Speed | When a developer runs Gherkin tests during TDD, the default `max_examples=1` must keep the suite fast | Total execution time for Gherkin tests must be dominated by `@Example` rows, not by generated examples | Must |
| QA2 | Isolation | When a project has both Gherkin and non-Gherkin Hypothesis tests, beehave's `max_examples=1` default must only affect Gherkin-decorated tests | Non-Gherkin Hypothesis tests must use Hypothesis's default (100) or developer-configured value | Must |
| QA3 | Configurability | When a developer wants more generation for CI, they can set `max_examples` in `pyproject.toml` | Configuration must be per-project, overridable per-test via `@settings` | Must |

---

## Pain Points Identified

- Hypothesis's default of 100 examples per test makes Gherkin test suites impractically slow during development
- Implementations hardcoded around test values are the primary concern — even one random example catches this
- Hypothesis `@example` (lowercase) and beehave `@Example` (uppercase) could be confused without clear naming

## Business Goals Identified

- Make Gherkin tests fast by default — `max_examples=1` keeps the suite responsive during TDD
- Separate Gherkin defaults from general Hypothesis defaults — beehave must not slow down non-Gherkin tests
- Use naming conventions to make the library boundary clear: capitalized = beehave, lowercase = Hypothesis

## Terms to Define (for glossary)

- **`@Example`** — beehave's decorator for explicit test cases from Gherkin Examples tables. Capitalized E distinguishes it from Hypothesis's `@example`. Converted to Hypothesis `@example` at collection time.
- **`max_examples`** — The number of randomly generated examples Hypothesis produces per test. beehave defaults to 1 for Gherkin-decorated tests (configurable in `pyproject.toml`). Explicit `@Example` rows are additive — they don't count toward this number.
- **Gherkin-decorated test** — A test function that uses @Given/@When/@Then/@And/@But decorators from beehave. Only these tests get beehave's default `max_examples=1`; regular Hypothesis tests are unaffected.

## Updates to Previous INs

### IN_20260510_beehave_design

- **Q8** (Gherkin-to-Hypothesis mapping): `@example` references updated to `@Example` (uppercase E) for beehave's decorator. Hypothesis's `@example` (lowercase) is a separate, parallel mechanism.
- **Q20** (Examples mapping): Updated — .feature Examples table rows become `@Example` decorators (uppercase E), not `@example`. These are converted to Hypothesis `@example` at collection time.

### IN_20260510_collection_mechanics

- **D7** (Hypothesis settings tags in .feature): Confirmed — settings do NOT go in .feature files. They belong in `pyproject.toml` or `@settings`. Only `@id:` tags go in .feature files.
- **D2** (@Example auto-generation): Updated — .feature Examples rows become `@Example` decorators (uppercase E), not `@example`.

## Action Items

- [ ] Define the `pyproject.toml` schema for beehave configuration (max_examples, feature_paths, strict mode, etc.)
- [ ] Design the collection-time mechanism that applies `max_examples=1` only to Gherkin-decorated tests
- [ ] Decide whether to create named profiles (beehave.dev, beehave.ci) or just set max_examples directly
- [ ] Confirm that `@Example` and `@example` can coexist on the same test function without conflict