# IN_20260510_step_decorator_runtime — Step Decorator Runtime Behavior

> **Status:** COMPLETE
> **Interviewer:** PO
> **Participant(s):** Project Founder
> **Session type:** Domain deep-dive

---

## General

| ID | Question | Answer |
|----|----------|--------|
| Q1 | What is the core problem this session addresses? | The previous design treated @When and @Then as purely structural annotations with no runtime effect. The founder challenged this: "I was hoping that when and then could do more than be only structural markers." If they're just labels, why not use comments? They need to provide tangible runtime value. |
| Q2 | What design principle emerged? | Step decorators serve two distinct roles: (1) collection-time metadata (validation, traceability, placeholder discovery) and (2) runtime report templates. The second role is what makes them genuinely useful rather than cosmetic. |
| Q3 | What was rejected and why? | Option A (strategies only on @Given): forces all strategy declarations onto @Given even for placeholders appearing in @Then, creating an awkward coupling. Option B (strategies on all decorators): makes @Then carry data generation semantics that don't belong there. Option D (namespace binding with `ctx` parameter): adds a `ctx` parameter to every test, adding ceremony. Option from previous session (purely structural decorators): rejected because it makes decorators equivalent to comments. Expression evaluation in @Then strings: rejected as reinventing Python's assert. |

## Domain Questions

| ID | Question | Answer |
|----|----------|--------|
| Q4 | What runtime value do step decorators provide? | They are **report templates**. On test failure, beehave renders each step's text with the actual placeholder values from the Hypothesis counterexample, producing a Gherkin-readable failure report. This makes Hypothesis counterexamples understandable by stakeholders who don't read Python. |
| Q5 | How does the "Then failed" heuristic work? | In Gherkin, assertions only live in Then steps. Given sets up, When acts, Then asserts. So if a test fails via `assert`, the failing Gherkin step is always the last @Then or @But. Given and When steps are marked ✓. Subsequent Then/But steps after the failure are marked "(not reached)". |
| Q6 | How are Given/When exceptions attributed? | When an exception (not an assertion) occurs, beehave uses a line-number heuristic: the test body is divided into three regions by convention — setup lines (Given), action lines (When), assertion lines (Then). The exception's traceback line number is mapped to the nearest region. If the exception occurs in the setup phase, it's attributed to @Given; if during action, to @When. This is a best-effort heuristic, not guaranteed correctness. The Gherkin report is supplementary context — the Python traceback always shows the exact line. |
| Q7 | What does the failure output look like? | On pass (initial=100, amount=30): all steps show ✓ with rendered values. On assertion failure (initial=5, amount=10): Given and When steps show ✓, the failing Then shows ✗ with the AssertionError. On exception (e.g., ValueError from User(balance=-1)): the Given step shows ✗ with the exception, subsequent steps show "(not reached)". All placeholder values are filled in from the Hypothesis counterexample. |
| Q8 | Why is this approach sufficient? | The 80/20 rule: 80% of failures are assertion failures (Then), 15% are action errors (When), 5% are setup errors (Given). For the 80% case, "mark the failing Then" is always correct. For the other 20%, line-number heuristics get it right almost always. The Gherkin report is additional context, not a replacement for the Python traceback. |
| Q9 | Does this add runtime overhead on pass? | No. Step tracking only activates on failure. Passing tests run at full Hypothesis speed with no beehave interception. |

## Feature: step-decorator-runtime

| ID | Question | Answer |
|----|----------|--------|
| Q10 | What is the full role of step decorators? | Two roles: (1) Collection-time: vocabulary validation, step ordering validation, placeholder discovery, @id traceability. (2) Runtime-on-failure: report templates that render `<placeholder>` values from Hypothesis counterexamples, producing stakeholder-readable Gherkin failure output. |
| Q11 | How does placeholder rendering work? | Each step decorator's text string contains `<placeholder>` tokens. On failure, beehave substitutes the actual values from the Hypothesis counterexample into the step text. `@Then("the balance should equal <initial> - <amount>")` with initial=5, amount=10 becomes `Then the balance should equal 5 - 10`. This produces a concrete Gherkin scenario for each failing example. |
| Q12 | How does beehave wrap the test function? | beehave wraps the test function in a try/except. Before execution, it renders all step texts with current placeholder values. On pass: all steps show ✓. On AssertionError: marks the failing @Then as ✗, subsequent steps as "(not reached)". On other exception: attributes to @Given or @When by line-number heuristic. |
| Q13 | What about multiple @Then/@But steps? | The first @Then that fails gets ✗. All subsequent @But/@Then steps show "(not reached)". This mirrors Python's execution model — an assertion failure stops the test. |
| Q14 | What about tests with no @Then? | Tests with only @Given + @When (setup + action, no assertion) are valid. If no exception occurs, all steps pass. If an exception occurs, it's attributed to the appropriate phase by line-number heuristic. |
| Q15 | Why not use explicit phase markers (with Given:/with When:/with Then:)? | Rejected because it adds ceremony. The convention-based line-ordering heuristic (setup before action before assertion) is correct often enough that explicit markers aren't worth the cost. The Gherkin report is supplementary context — if the heuristic is wrong, the Python traceback still shows the exact failing line. |

## Feature: strategy-resolution-update

| ID | Question | Answer |
|----|----------|--------|
| Q16 | What changed about strategy resolution? | Inline strategy kwargs on @Given are being dropped. All five decorators now take only a step text string — they are pure structural annotations at the syntax level. Strategy resolution is simplified to two levels: module-level variables (primary) and auto-inference from @example values (fallback). This decision is pending final founder confirmation. |

---

## Quality Attributes

| ID | Attribute | Scenario | Target | Priority |
|----|-----------|----------|--------|----------|
| QA1 | Reporting | When a Hypothesis test fails, beehave must produce a Gherkin-readable failure report showing which step failed and with what placeholder values | Failure output must render all `<placeholder>` values in step text; the failing step must be marked ✗; subsequent steps marked "(not reached)" | Must |
| QA2 | Performance | When tests pass, step tracking must add zero overhead | No try/except interception or value rendering on passing test runs; overhead limited to collection-time | Must |
| QA3 | Accuracy | When an assertion fails, the failing step must be attributed to the correct @Then decorator | The last @Then or @But before the assertion line is marked ✗; this is always correct for assertion failures | Must |
| QA4 | Best-effort attribution | When a non-assertion exception occurs, beehave should attribute it to the correct phase (Given/When) via line-number heuristic | Line-number heuristic should correctly attribute ≥90% of common exceptions; the Python traceback is always available as fallback | Should |

---

## Pain Points Identified

- Step decorators as purely structural labels provide no runtime value — they're equivalent to comments
- Hypothesis counterexamples are cryptic and unreadable by non-developers — they show Python values but not Gherkin context
- Existing BDD frameworks don't bridge the gap between Hypothesis's property-based counterexamples and stakeholder-readable Gherkin scenarios

## Business Goals Identified

- Make Hypothesis counterexamples readable by stakeholders through Gherkin-formatted failure reports
- Give step decorators genuine runtime value beyond collection-time validation
- Preserve the "plain Python" test body — no assertion DSL, no context managers, no framework ceremony in the test logic

## Terms to Define (for glossary)

- **Report template** — A step decorator's text string with `<placeholder>` tokens that gets rendered with actual values on test failure, producing a Gherkin-readable failure scenario
- **Then-failed heuristic** — The principle that assertion failures always occur in @Then steps; if a test fails via `assert`, the failing Gherkin step is always a @Then or @But
- **Line-number heuristic** — Best-effort attribution of non-assertion exceptions to @Given or @When phases based on the test body's line order (setup lines = Given, action lines = When, assertion lines = Then)

## Updates to Previous IN (IN_20260510_beehave_design)

- **Q12** (step decorator runtime role) is UPDATED: decorators are not purely structural at runtime. On failure, they serve as report templates rendering placeholder values into Gherkin-readable failure output.
- **Q14** (what step decorators don't do) is UPDATED: they don't execute step logic and don't wrap assertions, but they DO render failure reports. The "at runtime: nothing" answer is replaced by "at runtime: on failure, render step text with counterexample values."
- **QA1** (Performance) is UPDATED: runtime overhead is no longer zero — it's zero on pass, with report rendering only on failure.
- **Strategy resolution** is simplified to two levels: module-level variables (primary) and auto-inference from @example values (fallback). Inline kwargs on @Given are being dropped.

## Action Items

- [ ] Validate the "Then-failed" heuristic against real Hypothesis test suites to confirm ≥80% of failures are assertion failures
- [ ] Design the failure report output format (terminal, pytest integration, potential HTML)
- [ ] Confirm dropping inline strategy kwargs on @Given (simplifying strategy resolution to module-level → auto-infer)
- [ ] Investigate how Hypothesis's reporting hooks (e.g., `report_example`) can be leveraged for step rendering
- [ ] Update product definition with step decorator runtime behavior