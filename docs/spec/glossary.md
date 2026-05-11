# Glossary: beehave

> Living glossary of domain terms used in this project.
> Written and maintained by the Domain Expert during Discovery.
> Append-only: never edit or remove past entries. If a term changes, mark it retired in favor of the new entry and write a new entry.
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

## @Background

**Definition:** A decorator that references a background fixture function providing shared Given/When/Then setup steps and their parameters for multiple scenarios.

**Aliases:** none

**Example:** `@Background(background_balance_accounting)` references a fixture with `@Given("a user with balance <initial>")` that multiple test functions share.

**Source:** 2026-05-10

## @Example

**Definition:** A beehave decorator (uppercase E) that provides explicit test values from Gherkin Examples tables, converted to Hypothesis @example (lowercase e) at import time. Keyword-first: `@Example(initial=100, amount=30, remaining=70)`. Positional shorthand: `@Example(100, 30, 70)` mapping left-to-right by placeholder appearance order. Mixed keyword + positional is not allowed.

**Aliases:** none

**Example:** `@Example(initial=100, amount=30, remaining=70)` provides explicit test values; `@Example(100, 30, 70)` does the same using positional shorthand.

**Source:** 2026-05-10

## @id tag

**Definition:** A tag in the format `@id:<value>` on a Gherkin scenario that links it to a Python test function via the function name suffix.

**Aliases:** none

**Example:** `@id:kx7m2p9q` on a scenario links to `test_balance_calculation_kx7m2p9q`.

**Source:** 2026-05-10

## beehave generate

**Definition:** A beehave CLI command that creates test stub files for orphan scenarios, processing all .feature files by default or a single named feature, appending to existing files with interactive confirmation (TTY) or auto-append (non-TTY / --json), safe and idempotent, reporting parse errors and skipping malformed files.

**Aliases:** none

**Example:** Running `beehave generate` processes all .feature files and creates test stubs for any orphan scenarios found.

**Source:** 2026-05-10

## Adoption Level

**Definition:** A progressive opt-in model with two levels: (1) decorators only — validates step ordering and placeholder-parameter matching, (2) add .feature traceability — adds step text matching, @id traceability, and orphan detection.

**Aliases:** none

**Example:** A team starts at level 1 with just @Given/@When/@Then decorators and no .feature files, then adds .feature files for full traceability at level 2.

**Source:** 2026-05-10

## Collection-Time Validation

**Definition:** Validation of step text, ordering, placeholders, and @id links that runs during pytest collection (or via CLI commands), not at test runtime. Zero runtime overhead on passing tests.

**Aliases:** none

**Example:** Step text mismatches, ordering violations, and orphan tests are reported at collection time, not during test execution.

**Source:** 2026-05-10

## Exact Step Matching

**Definition:** A validation rule requiring step text in decorators to match .feature step text character-for-character (after stripping keywords and tokenizing placeholders). No fuzzy matching, no normalization.

**Aliases:** none

**Example:** `@Given("a user with balance <initial>")` must exactly match `Given a user with balance <initial>` in the .feature file. A typo like "an balance" is a validation error.

**Source:** 2026-05-10

## ExamplesTable

**Definition:** A table of explicit test values from the .feature file, represented as a Value Object in the Feature Parsing bounded context, mapping to Hypothesis @example decorators.

**Aliases:** none

**Example:** An Examples table with `| initial | amount | remaining |` rows maps to `@Example(initial=100, amount=30, remaining=70)` decorators.

**Source:** 2026-05-10

## FeatureFile

**Definition:** A parsed .feature file containing Feature, Rule, Scenario, and Steps, serving as the Aggregate root in the Feature Parsing bounded context and the source of truth for traceability. Maps 1:1 to a TestDirectory containing one TestModule per Rule (or default_test.py if no Rules).

**Aliases:** none

**Example:** `balance_accounting.feature` is parsed into a FeatureFile containing all scenarios and their steps for traceability validation.

**Source:** 2026-05-10

## Gherkin Rule

**Definition:** A Gherkin Rule block that groups related scenarios within a FeatureFile, represented as a Value Object in the Feature Parsing bounded context; normalized to snake_case for test module naming.

**Aliases:** Rule block

**Example:** Rule "Total calculation" in balance_accounting.feature maps to test module total_calculation_test.py.

**Source:** 2026-05-11

## Gherkin-Decorated Test

**Definition:** A test function that uses @Given/@When/@Then/@And/@But decorators from beehave. Only these tests get beehave's default max_examples=1; regular Hypothesis tests are unaffected.

**Aliases:** none

**Example:** Any function with `@Given`, `@When`, or `@Then` decorators is a Gherkin-decorated test.

**Source:** 2026-05-10

## Idempotent (CLI command)

**Definition:** A beehave CLI command where running it N times produces the same result as running it once; for generate, scenarios with existing test functions are skipped, and for sync, scenarios with existing @id tags keep them. See also: Safe (CLI command).

**Aliases:** none

**Example:** Running `beehave generate` twice produces the same test stubs as running it once — scenarios already covered are skipped.

**Source:** 2026-05-10

## Import-Time Application

**Definition:** The mechanism by which @Given resolves strategies and applies Hypothesis decorators when the module is imported, not at runtime or collection time. Standard Python decorator mechanics.

**Aliases:** none

**Example:** When Python imports a test module, @Given (the outermost decorator) collects step metadata, resolves strategies from module scope, and applies hypothesis.given().

**Source:** 2026-05-10

## Mismatch

**Definition:** A difference between decorator step text and .feature step text, represented as a Value Object in the Validation bounded context, carrying the expected text and actual text for precise error reporting.

**Aliases:** none

**Example:** A decorator says `@Given("a user with an balance")` while the .feature says `Given a user with balance` — the Mismatch carries expected "a user with balance <initial>" and actual "a user with an balance <initial>".

**Source:** 2026-05-10

## One Function, One Scenario

**Definition:** The principle that each test function corresponds to exactly one Gherkin scenario, with all steps (Given/When/Then/And/But) as decorators on that single function. No step definition files.

**Aliases:** none

**Example:** `test_balance_calculation_kx7m2p9q` has @Given, @When, @Then decorators for all steps in one function, rather than scattering steps across multiple step definition files.

**Source:** 2026-05-10

## Orphan Scenario

**Definition:** A .feature scenario whose @id has no matching Python test function. Flagged at collection time or via CLI commands.

**Aliases:** none

**Example:** A scenario tagged `@id:m3n4o5p6` with no test function ending in `_m3n4o5p6`.

**Source:** 2026-05-10

## Orphan Test

**Definition:** A Python test function whose @id suffix has no matching .feature scenario. Flagged at collection time or via CLI commands.

**Aliases:** none

**Example:** `test_withdrawal_rules_a1b2c3d4` where no .feature scenario has `@id:a1b2c3d4`.

**Source:** 2026-05-10

## Placeholder

**Definition:** A `<placeholder>` token in step text that maps to a Hypothesis strategy, represented as a Value Object in the Feature Parsing bounded context.

**Aliases:** none

**Example:** `<initial>` in `Given a user with balance <initial>` is a Placeholder resolved via Strategy Resolution.

**Source:** 2026-05-10

## Random Permanent ID

**Definition:** An 8-character randomly generated ID assigned once by `beehave sync` and never changed. Editing scenario text does not affect the ID. Not derived from scenario content.

**Aliases:** none

**Example:** `@id:kx7m2p9q` is assigned once and remains stable even if the scenario text changes.

**Source:** 2026-05-10

## Report Template

**Definition:** A step decorator's text string with <placeholder> tokens that gets rendered with actual values on test failure, producing a Gherkin-readable failure scenario. Assertion failures are attributed to @Then or @But (Then-failed heuristic); non-assertion exceptions are attributed to the step region by body line order (line-number heuristic).

**Aliases:** none

**Example:** `@Then("the balance should equal <remaining>")` with remaining=70 renders as "Then the balance should equal 70" on failure.

**Source:** 2026-05-10

## Runner-Agnostic Core

**Definition:** The beehave library that works without any specific test runner. Uses Hypothesis directly for @given application and failure reporting. Integration with pytest (or other runners) is an optional plugin.

**Aliases:** none

**Example:** The core library applies @given at import time via the @Given decorator, without importing pytest.

**Source:** 2026-05-10

## Safe (CLI command)

**Definition:** A beehave CLI command that only adds content and never modifies or deletes existing content; safe commands (sync, generate) don't require --dry-run or confirmation for their primary operation, following a risk escalation hierarchy: safe (sync, generate) → moderate (fix) → destructive (clean). See also: Idempotent (CLI command).

**Aliases:** none

**Example:** `beehave sync` only adds @id tags and never removes or changes existing ones, making it a safe command.

**Source:** 2026-05-10

## Scenario

**Definition:** A Gherkin scenario with @id tag, steps, and Examples table, represented as an Entity in the Feature Parsing bounded context; one function per scenario is beehave's core principle.

**Aliases:** none

**Example:** A scenario tagged `@id:kx7m2p9q` with Given/When/Then steps maps to a single test function `test_balance_calculation_kx7m2p9q`.

**Source:** 2026-05-10

## Step

**Definition:** A Gherkin step with keyword (Given/When/Then/And/But), text, and placeholders, represented as a Value Object in the Feature Parsing bounded context. @And/@But steps inherit their effective step type (Given/When/Then) from the preceding keyword for ordering validation.

**Aliases:** none

**Example:** `Given a user with balance <initial>` is a Step with keyword "Given", text, and one Placeholder. `And the balance is positive` following `Given` inherits effective keyword "Given".

**Source:** 2026-05-10

## Effective Keyword

**Definition:** The resolved Given/When/Then keyword that an @And/@But step inherits from the most recent preceding Given/When/Then step for ordering validation purposes.

**Aliases:** inherited keyword

**Example:** In a sequence @Given, @And, @When, @And — the first @And inherits "Given", the second @And inherits "When".

**Source:** 2026-05-11

## Step Decorator

**Definition:** One of @Given, @When, @Then, @And, @But; a collection-time annotation that links a test function to a Gherkin step, validates vocabulary, and discovers placeholders. At import time, @Given also resolves strategies and applies hypothesis.given(). At runtime on failure, serves as a report template rendering <placeholder> values from the Hypothesis counterexample into stakeholder-readable Gherkin output.

**Aliases:** none

**Example:** `@Given("a user with balance <initial>")` annotates the test function with step metadata and, as the outermost decorator, resolves `initial` from module scope and applies `hypothesis.given(initial=initial)`.

**Source:** 2026-05-10

## Strategy Resolution

**Definition:** The mechanism for connecting <placeholder> names to Hypothesis strategies: module-level variables (primary, explicit) → inference from @Example value types (secondary) → st.integers() fallback (configurable to error).

**Aliases:** none

**Example:** `initial = st.integers(min_value=0)` at module scope resolves `<initial>` explicitly. If missing, `@Example(initial=100)` infers `st.integers()` from the int type.

**Source:** 2026-05-10

## Test function (informal)

**Definition:** Developer-facing term for a function with beehave step decorators; see formal term: Gherkin-Decorated Test.

**Aliases:** none

**Example:** "Write a test function for that scenario" means write a Gherkin-Decorated Test.

**Source:** 2026-05-10

## Test Directory

**Definition:** A directory under tests/features/ named after the feature slug (snake_case), containing one or more test modules; one directory per FeatureFile (1:1 mapping).

**Aliases:** none

**Example:** tests/features/balance_accounting/ is the test directory for balance_accounting.feature.

**Source:** 2026-05-11

## Test Module

**Definition:** A Python test file derived from a FeatureFile + Rule mapping, following the naming convention tests/features/<feature_slug>/<rule_name>_test.py (or default_test.py when no Gherkin Rule exists).

**Aliases:** none

**Example:** total_calculation_test.py is the test module for the "Total calculation" Rule in balance_accounting.feature.

**Source:** 2026-05-11

## Test stub

**Definition:** A Python file generated by `beehave generate` for an orphan scenario, containing imports (hypothesis strategies, beehave decorators), module-level strategy variables for all `<placeholders>` (defaulting to `st.integers()`), step decorators matching .feature steps, @Example decorators from .feature Examples table, and a function with `...` body named `test_<scenario_title_snake_case>_<id>`, immediately importable and collectable by pytest.

**Aliases:** skeleton (deprecated)

**Example:** `beehave generate` produces a test stub with `def test_withdrawal_insufficient_funds_a1b2c3d4(): ...` ready for pytest collection.

**Source:** 2026-05-10

## Unified Parameterization

**Definition:** The principle that every scenario uses <placeholders> with @Example values; a simple Scenario is just one with a single @Example, eliminating the Scenario vs Scenario Outline distinction.

**Aliases:** none

**Example:** Both `@Example(initial=100)` (one value) and `@Example(initial=100) @Example(initial=0)` (multiple values) use the same <placeholder> + @Example pattern.

**Source:** 2026-05-10

## ValidationReport

**Definition:** A report of mismatches, orphans, and ordering violations, represented as an Entity in the Validation bounded context.

**Aliases:** none

**Example:** Running `beehave validate` produces a ValidationReport listing all step text mismatches, orphan scenarios, and ordering violations.

**Source:** 2026-05-10

## Vocabulary Enforcement

**Definition:** Validating that step text in decorators matches known domain terms from .feature files, preventing vocabulary drift. Exact matching (no fuzzy, no normalization).

**Aliases:** none

**Example:** If the .feature says "Given a user with balance" and the test says "Given a user with an balance", beehave flags the mismatch.

**Source:** 2026-05-10

## FailureReport

**Definition:** A Gherkin-readable failure scenario rendered from a Hypothesis counterexample, represented as an Entity and Aggregate root in the Reporting bounded context, composed of StepReport lines with one failing step and subsequent steps marked "(not reached)."

**Aliases:** none

**Example:** When a test fails with initial=5, amount=10, the FailureReport shows "Given a user with balance 5 ✓ / When the user spends 10 ✓ / Then the balance should equal -5 ✗ (AssertionError)".

**Source:** 2026-05-11

## StepReport

**Definition:** A rendered step in a FailureReport showing ✓ (passed), ✗ (failed with exception), or "(not reached)" (after a failure), with placeholder values filled from the Hypothesis counterexample.

**Aliases:** none

**Example:** "Then the balance should equal -5 ✗ (AssertionError)" is a StepReport showing a failed assertion.

**Source:** 2026-05-11

## Then-failed Heuristic

**Definition:** A failure attribution rule where AssertionError exceptions are always attributed to @Then (or @But), regardless of where in the test body the assert statement actually resides. Known limitation: assertion failures in @Given/@When bodies are also attributed to @Then.

**Aliases:** none

**Example:** An assert statement in a When step body still produces a report showing the Then step as ✗.

**Source:** 2026-05-11

## Line-number Heuristic

**Definition:** A failure attribution rule where non-assertion exceptions are attributed to the step region (@Given, @When, or @Then) where the exception occurs by body line order.

**Aliases:** none

**Example:** A ValueError raised on line 12 of a test body, where lines 10-15 correspond to the Given step region, is attributed to @Given.

**Source:** 2026-05-11
