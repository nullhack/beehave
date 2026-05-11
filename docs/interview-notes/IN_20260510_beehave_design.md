# IN_20260510_beehave_design — Core Product Design Decisions

> **Status:** COMPLETE
> **Interviewer:** PO
> **Participant(s):** Project Founder
> **Session type:** Initial discovery

---

## General

| ID | Question | Answer |
|----|----------|--------|
| Q1 | Who are the users? | Property-based TDD developers using Hypothesis who want Gherkin structure; QA engineers writing .feature files who need traceability to tests; team leads wanting vocabulary enforcement across test suites. |
| Q2 | What does the product do at a high level? | A thin Python layer that adds Gherkin-style step decorators (@Given, @When, @Then, @And, @But) to Hypothesis-based tests, with vocabulary validation at pytest collection time and traceability linking test functions to .feature scenarios via @id tags. It also provides a Gherkin parser that maps Scenario Outline + Examples to Hypothesis @example + @given. |
| Q3 | Why does it exist — what problem does it solve? | Existing BDD frameworks (pytest-bdd, behave) force splitting one scenario across multiple step definition functions, requiring exact string matching that makes Gherkin verbose and brittle. beehave eliminates this with the "one function, one scenario" principle and @id linking instead of string matching. It also enforces vocabulary consistency at collection time rather than relying on developers to manually keep step text in sync. |
| Q4 | When and where is it used? | During test authoring (developers writing tests in their IDE) and CI runs (pytest collection-time validation). Vocabulary and step ordering validation happen at collection time with zero runtime overhead. |
| Q5 | Success — what does "done" look like? | Developers can write Gherkin-structured Hypothesis tests without ceremony — just decorators and assert. Every .feature scenario traces to a test function via @id. Vocabulary is enforced automatically. Progressive adoption works: start with decorators only, add traceability and property-based testing incrementally. |
| Q6 | Failure — what must never happen? | Tests must never have runtime overhead from vocabulary validation (all validation is collection-time). Step definitions must never be split across multiple functions (one function, one scenario). Exact string matching must never be required for traceability (@id linking replaces it). The framework must never wrap Hypothesis — it composes alongside it. |
| Q7 | Out-of-scope — what are we explicitly not building? | NOT an assertion DSL (Python's assert is sufficient). NOT natural language processing or synonym resolution (vocabulary enforcement means exact terms, no synonyms). NOT a step definition runner (test body is plain Python). NOT domain model introspection (decouples test library from domain code). NOT a full BDD framework replacing behave/pytest-bdd (no .feature file execution). NOT a monolithic @gherkin decorator (composes with Hypothesis, doesn't wrap it). |

## Domain Questions

| ID | Question | Answer |
|----|----------|--------|
| Q8 | How does beehave map Gherkin Scenario Outline to Hypothesis? | A Scenario Outline with an Examples table maps to Hypothesis @given (from strategy variables matching placeholder names) and @example (from each row in the Examples table). beehave generates these at collection time by parsing the .feature file. The test body is untouched — beehave only adds Hypothesis decorators. **Note:** Hypothesis settings tags in .feature files (e.g., `@max-examples:500`) are deferred — .feature files only have `@id:` tags for now. |
| Q9 | Why is there no distinction between Scenario and Scenario Outline? | Every scenario uses `<placeholders>`. A "simple" Scenario is just one with a single @example. This unified parameterization eliminates the confusing Scenario vs Scenario Outline distinction. Before beehave, developers had to choose between two inconsistent styles; now there is one consistent pattern: all placeholders, all the time. |
| Q10 | How does strategy resolution work for `<placeholder>` variables? | Two levels, from least to most ceremony: (1) Module-level variables — `initial = st.integers(min_value=0)` in module scope, beehave resolves `<initial>` by finding `initial` in the module. (2) Infer from @Example values — if no strategy is defined and @Example values exist, beehave infers the strategy from the value type (`100` → `st.integers()`, `"Alice"` → `st.text()`, `True` → `st.booleans()`). Fallback: `st.integers()` (configurable to error in `pyproject.toml`). No inline kwargs, no naming convention heuristics. |
| Q11 | How does @id linking work between .feature files and test functions? | The @id tag in the .feature file is the single connection point: (1) .feature file has `@id:a1b2c3d4` on a scenario, (2) Python test function is named `test_*_a1b2c3d4`, (3) beehave parses the .feature file, finds the scenario, extracts steps and placeholders, (4) at collection time: validates decorator steps match .feature steps, validates all `<placeholder>` names have strategies or @example values, validates step ordering. No string matching required. |
| Q12 | What do the step decorators actually do at runtime vs collection time? | At collection time: (1) traceability — link the test to the .feature scenario via @id convention, (2) vocabulary validation — verify step text matches known domain terms, (3) step ordering validation — ensure Given before When before Then, (4) placeholder discovery — extract `<placeholder>` names and connect to strategy mappings and @example values. At runtime: on failure, step decorators serve as report templates — they render `<placeholder>` values from the Hypothesis counterexample into stakeholder-readable Gherkin failure output. They don't execute step logic (that's in the test body), they don't wrap assertions (use Python's assert), they don't replace @given from Hypothesis (that's data generation). |

## Feature: step-decorators

| ID | Question | Answer |
|----|----------|--------|
| Q13 | What are the step decorators and why these five? | The five Gherkin step keywords, capitalized to match Gherkin convention: @Given (precondition/data setup), @When (action/event), @Then (expected outcome), @And (continues previous step type), @But (contrastive continuation). These map 1:1 to Gherkin keywords. No more, no fewer. Rejected: 30+ verb lists (confuses step keywords with step text), when(**kwargs)/then(**kwargs) API (unreadable, un-Pythonic). |
| Q14 | What do step decorators NOT do? | They don't execute step logic — that lives in the test body. They don't wrap assertions — Python's assert handles that. They don't replace Hypothesis @given — that remains data generation. At collection time they are metadata; at runtime they only render failure reports. They do NOT intercept or modify test execution. |
| Q15 | How do step decorators compose with Hypothesis? | beehave generates @given(...) from strategy variables matching `<placeholder>` names, and @example(...) from the .feature Examples table. The test body is plain Python. The decorators compose alongside Hypothesis, they don't wrap it. |

## Feature: id-traceability

| ID | Question | Answer |
|----|----------|--------|
| Q16 | How does @id linking replace string matching? | Instead of pytest-bdd-style exact string matching between step definitions and .feature text, beehave uses @id tags as the single connection point. The .feature file tags a scenario with `@a1b2c3d4`, the test function is named `test_*_a1b2c3d4`. This eliminates brittleness from text changes and allows step text to evolve independently as long as the @id stays stable. |
| Q17 | What validation happens at collection time for @id? | beehave parses the .feature file, finds the scenario by @id, extracts its steps and placeholders, then validates: (1) decorator steps match .feature steps, (2) all `<placeholder>` names have strategies or @example values, (3) step ordering (Given before When before Then). All validation is collection-time, zero runtime cost. |

## Feature: strategy-resolution

| ID | Question | Answer |
|----|----------|--------|
| Q18 | How does strategy resolution work in practice? | Level 1 (explicit): Define `initial = st.integers(min_value=0)` at module scope. beehave finds it by name matching `<initial>`. Level 2 (infer from @Example): If no strategy exists and @Example values are present, beehave infers from value type (`int` → `st.integers()`, `str` → `st.text()`, `bool` → `st.booleans()`). Level 3 (fallback): `st.integers()` default, configurable to error in `pyproject.toml`. No inline kwargs on decorators. No naming convention heuristics. |
| Q19 | Why module-level variables as the primary strategy mechanism? | Zero ceremony. A developer writes `initial = st.integers(min_value=0)` exactly as they would with Hypothesis, and beehave resolves `<initial>` by finding that name in module scope. No registration, no configuration, no ceremony. The variable name IS the mapping. |

## Feature: examples-mapping

| ID | Question | Answer |
|----|----------|--------|
| Q20 | How do .feature Examples map to @example decorators? | Each row in the .feature Examples table becomes one `@example(...)` decorator on the test function. beehave can auto-generate these from the .feature file. Combined with unified parameterization, this means every scenario — whether it has one example or many — uses the same `<placeholder>` + `@example` pattern. No Scenario vs Scenario Outline distinction. |

## Feature: collection-time-validation

| ID | Question | Answer |
|----|----------|--------|
| Q21 | What validations run at collection time? | (1) Vocabulary validation — step text in decorators matches known domain terms from glossary/feature files. (2) Step ordering — Given before When before Then. (3) @id traceability — decorator steps match .feature steps for the linked scenario. (4) Placeholder completeness — all `<placeholder>` names have strategies or @example values. **Note:** Hypothesis settings tags in .feature files are deferred — not part of collection-time validation for now. |
| Q22 | Why collection time and not runtime? | Zero runtime overhead. Tests run at full Hypothesis speed with no beehave interception. Validation failures surface immediately when pytest collects tests, not during test execution. This is a core quality attribute: vocabulary enforcement must never slow down a test suite. |

## Feature: progressive-adoption

| ID | Question | Answer |
|----|----------|--------|
| Q23 | What are the adoption levels? | Level 1 (start): Write tests with just @Given, @When, @Then decorators and assert. No .feature file required. Level 2 (add traceability): Add @id tags to .feature files and function names. Level 3 (add property-based testing): Define strategy variables for `<placeholder>` names. Level 4 (add validation): Enable vocabulary validation and step matching against .feature files. Each level is opt-in per test. |
| Q24 | Why is progressive adoption important? | Teams can start with zero ceremony — just decorators and assert — and incrementally adopt traceability, property-based testing, and validation. No big-bang migration. No requirement to have .feature files on day one. This lowers the barrier to entry and allows teams to adopt beehave at their own pace. |

---

## Quality Attributes

| ID | Attribute | Scenario | Target | Priority |
|----|-----------|----------|--------|----------|
| QA1 | Performance | When pytest collects tests, vocabulary and step validation runs during collection phase; on test failure, step text is rendered with counterexample values for Gherkin-readable output | Collection-time validation must add <1ms per test to collection; runtime overhead must be zero on pass, report rendering only on failure | Must |
| QA2 | Composability | When a developer uses beehave decorators alongside Hypothesis @given, @example, and @settings, both work together without conflict | beehave decorators must compose with all standard Hypothesis decorators; no wrapping or interception of Hypothesis internals | Must |
| QA3 | Progressive Adoption | When a developer writes a test with only @Given/@When/@Then decorators and no .feature file, the test must still run correctly | Tests must work at adoption level 1 (decorators only) without .feature files, strategy variables, or @example values | Must |
| QA4 | Correctness | When pytest collects a test with an @id tag, beehave must validate the link between the .feature scenario and the test function | @id linking must be validated at collection time; mismatches must produce clear error messages identifying the .feature file, scenario, and test function | Must |
| QA5 | Usability | When a developer writes a test with `<placeholder>` names, beehave must resolve strategies with zero configuration for the common case | Module-level variable resolution must work by name matching without registration or configuration | Should |

---

## Pain Points Identified

- Existing BDD frameworks (pytest-bdd, behave) force splitting one scenario across multiple step definition functions, making tests hard to navigate and maintain
- Exact string matching between step definitions and .feature text is brittle — any text change breaks the link
- The Scenario vs Scenario Outline distinction in Gherkin is confusing and leads to inconsistent test patterns
- Step definition files scatter scenario logic across multiple locations, losing the narrative flow
- Vocabulary drift across test suites goes undetected until manual review

## Business Goals Identified

- Provide the simplest possible API for Gherkin-structured Hypothesis testing (one function, one scenario)
- Enforce vocabulary consistency automatically at collection time, not through manual review
- Enable progressive adoption so teams can start with decorators only and add traceability and property-based testing incrementally
- Compose with Hypothesis rather than wrapping it, preserving Hypothesis's power and ergonomics
- Eliminate the need for step definition files entirely

## Terms to Define (for glossary)

- **Step decorator** — One of @Given, @When, @Then, @And, @But; a collection-time annotation that links a test function to a Gherkin step, validates vocabulary, and discovers placeholders. At runtime on failure, serves as a report template rendering `<placeholder>` values from the Hypothesis counterexample into stakeholder-readable Gherkin output.
- **Unified parameterization** — The principle that every scenario uses `<placeholders>` with `@example` values; a simple Scenario is just one with a single @example, eliminating the Scenario vs Scenario Outline distinction
- **Strategy resolution** — The two-level mechanism for connecting `<placeholder>` names to Hypothesis strategies: module-level variables (primary, explicit) or inference from @Example value types (secondary, implicit). Fallback: `st.integers()` (configurable to error). No inline kwargs, no naming convention heuristics.
- **@id linking** — The traceability mechanism connecting .feature scenarios to test functions via `@id:value` tags, replacing string matching. The `id:` prefix makes it parseable and distinct from other tag types.
- **Collection-time validation** — All vocabulary, ordering, traceability, and placeholder checks run during pytest collection, not at test runtime
- **Progressive adoption** — The four-level opt-in model: (1) decorators only, (2) add @id traceability, (3) add strategy variables, (4) add vocabulary validation
- **Vocabulary enforcement** — Validating that step text in decorators matches known domain terms from glossary or .feature files, preventing vocabulary drift

## Action Items

- [ ] Create product definition document capturing these design decisions
- [ ] Define ubiquitous language glossary with the terms identified above
- [ ] Draft feature specifications for each of the six feature areas
- [ ] Validate unified parameterization design against Hypothesis internals
- [ ] Investigate pytest collection hooks needed for vocabulary and step validation