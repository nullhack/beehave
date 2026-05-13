# IN_20260510_integration_decisions — Integration & Final Pre-Development Decisions

> **Status:** COMPLETE
> **Interviewer:** PO
> **Participant(s):** Project Founder
> **Session type:** Architecture decision

---

## General

| ID | Question | Answer |
|----|----------|--------|
| Q1 | What is this session about? | Final pre-development decisions on three topics: collection-time validation integration (how step text validation hooks into the system), failure report integration (how Gherkin-readable failure reports reach the developer), and @Example format (positional vs keyword). |
| Q2 | What is the overarching principle? | Runner-agnostic core, runner-specific integration layer. The core library uses Hypothesis directly and has no pytest dependency. Integration with pytest (and other runners) is an optional plugin. |

## Collection-Time Validation Integration

| ID | Question | Answer |
|----|----------|--------|
| Q3 | How does beehave validate step text against .feature files? | **CLI-based validation** as part of `beehave sync` and `beehave fix`. These commands parse .feature files, match step text, report mismatches, and optionally fix them. Validation happens when the developer runs a CLI command, not during test collection. |
| Q4 | What about real-time validation during pytest collection? | **Deferred to a future pytest plugin** (`pytest_beehave`). The core library provides validation logic that any integration layer can call. The pytest plugin will hook into `pytest_collection_modifyitems` to provide real-time warnings during test collection. This is not part of the core library. |
| Q5 | Why CLI-first for validation? | (1) Runner-agnostic — works with any test runner. (2) Separation of concerns — validation is a sync/check operation, not a runtime concern. (3) Progressive adoption — developers can use CLI validation before setting up the pytest plugin. |

## Failure Report Integration

| ID | Question | Answer |
|----|----------|--------|
| Q6 | How do Gherkin-readable failure reports reach the developer? | **Hypothesis's `report_example` callback.** When a test fails, Hypothesis calls `report_example` with the failing input. beehave registers a callback that renders step text with counterexample values, producing the Gherkin-readable failure report. This is runner-agnostic — it works with any test runner that executes Hypothesis tests. |
| Q7 | What is the architecture for failure reporting? | Core library provides `beehave.format_failure(test_function, exception, inputs)` that produces a Gherkin-readable string. The Hypothesis callback uses this internally. Future integration layers (pytest plugin, etc.) can call this function and format the output for their runner (colors, terminal width, etc.). |
| Q8 | Why Hypothesis's callback and not pytest hooks? | (1) Runner-agnostic — works with any test runner that uses Hypothesis. (2) Hypothesis already provides the failure input (counterexample values) — we just need to render it. (3) No pytest dependency in the core library. (4) The pytest plugin can enhance presentation later (colors, formatting) without changing the core. |

## @Example Format

| ID | Question | Answer |
|----|----------|--------|
| Q9 | What is the @Example format? | **Keyword-first.** The primary form uses keyword arguments matching `<placeholder>` names. Positional arguments are supported as shorthand. Mixed keyword + positional is not allowed. |
| Q10 | What does keyword form look like? | `@Example(initial=100, amount=30, remaining=70)`. Each keyword matches a `<placeholder>` name in the step text. Order-independent — the keywords map to placeholders by name. |
| Q11 | What does positional shorthand look like? | `@Example(100, 30, 70)`. Values map to `<placeholder>` names left-to-right by appearance in step text. `@Example(100, 30, 70)` with steps `@Given("a user with balance <initial>") @When("the user spends <amount>") @Then("the balance should equal <remaining>")` maps to initial=100, amount=30, remaining=70. |
| Q12 | Why no mixed form? | Mixed positional + keyword in the same `@Example` call is confusing and error-prone. If someone writes `@Example(100, 30, remaining=70)`, they're probably making a mistake about which position maps to which placeholder. Each @Example call must be either all positional or all keyword. |
| Q13 | What is the recommended form? | **Keyword-first.** Developers should prefer keyword form for readability. Positional form is shorthand for simple cases with few placeholders. beehave documentation and generated stubs should use keyword form. |

## Positional Mapping Order

| ID | Question | Answer |
|----|----------|--------|
| Q14 | How do positional @Example values map to placeholders? | **Left-to-right by first appearance in step text.** The first value maps to the first `<placeholder>` encountered when reading step decorators top-to-bottom. `@Given("a user with balance <initial>") @When("the user spends <amount>") @Then("the balance should equal <remaining>")` — positional order is initial, amount, remaining. |

## Complete Decision Summary

| # | Decision | Resolution |
|---|----------|------------|
| 1 | ID generation | Random 8-char, permanent once generated |
| 2 | @Example format | Keyword-first, positional shorthand, no mixed |
| 3 | Positional mapping order | Left-to-right by first appearance in step text |
| 4 | Strategy resolution | Module-level variable → @Example type inference → `st.integers()` fallback |
| 5 | Inline kwargs on @Given | Dropped — all five decorators take only step text |
| 6 | @given application | Import-time via @Given decorator (runner-agnostic) |
| 7 | @Background | Fixture with step decorators, all params in test signature |
| 8 | Failure reporting | Hypothesis `report_example` callback (core), pytest plugin (later) |
| 9 | Collection-time validation | CLI commands (sync/fix), pytest plugin (later) |
| 10 | @And/@But ordering | Decorator stack position determines step type |
| 11 | Feature file structure | 1:1 mapping, one .feature per feature directory |
| 12 | CLI commands | sync (safe), generate (safe), fix (moderate), clean (destructive) |
| 13 | Strategy type inference | No naming convention heuristics; type from @Example values |
| 14 | @id tags | Random permanent IDs owned by beehave |
| 15 | Step matching | Exact (no fuzzy), character-for-character |
| 16 | max_examples default | 1 for Gherkin-decorated tests, configurable in pyproject.toml |
| 17 | Progressive adoption | Level 1 (decorators only) → Level 2 (@id traceability) → Level 3 (strategies) → Level 4 (vocabulary validation) |
| 18 | .feature tags | Only `@id:` tags for now; settings in pyproject.toml |

---

## Quality Attributes

| ID | Attribute | Scenario | Target | Priority |
|----|-----------|----------|--------|----------|
| QA1 | Runner-agnosticism | When beehave core is imported, it must not import pytest | The core library (decorators, strategy resolution, parser, validation, CLI, reporting) must have zero pytest dependencies | Must |
| QA2 | Keyword clarity | When a developer reads @Example, they can immediately identify which value maps to which placeholder | Keyword form is self-documenting; positional form follows a clear left-to-right convention | Must |
| QA3 | Progressive integration | When a developer uses beehave without the pytest plugin, CLI validation and Hypothesis reporting must still work | Core features (decorators, @given application, CLI, reporting) must work without pytest installed | Must |

---

## Pain Points Identified

- Mixing positional and keyword @Example arguments creates ambiguity about which value maps to which placeholder — rejected to avoid confusion
- Tying core functionality to pytest hooks would violate Hypothesis's runner-agnostic design and limit beehave to pytest users
- Failure reporting must work without pytest — Hypothesis's own hooks provide the integration point

## Business Goals Identified

- Keep the core library runner-agnostic — Hypothesis is the only required dependency for core functionality
- Use Hypothesis's own extension points (callbacks, decorators) rather than test-runner-specific hooks for core features
- Make pytest integration an optional enhancement, not a requirement

## Terms to Define (for glossary)

- **Keyword-first @Example** — `@Example(initial=100, amount=30, remaining=70)` where keyword names match `<placeholder>` names. The recommended form for readability.
- **Positional @Example** — `@Example(100, 30, 70)` where values map left-to-right by first appearance in step text. Shorthand for simple cases.
- **Hypothesis report_example callback** — The mechanism by which beehave integrates failure reporting. Hypothesis calls this callback with failing inputs; beehave renders step text with counterexample values.
- **Runner-agnostic core** — The beehave library that works without any specific test runner. Uses Hypothesis directly. Integration with pytest (or other runners) is an optional plugin.

## Updates to Previous INs

### IN_20260510_architecture

- **D1** (collection-time validation integration): Resolved — CLI-based validation via sync/fix commands. Future pytest plugin for real-time collection warnings.
- **D2** (failure report integration): Resolved — Hypothesis `report_example` callback for core reporting. Future pytest plugin for enhanced presentation.

### IN_20260510_adversarial_review

- **O1** (@Example positional mapping order): Resolved — left-to-right by first appearance in step text. Keyword form is recommended.
- **O3** (how does beehave inject Hypothesis @given): Resolved — import-time via @Given decorator (IN_20260510_architecture).
- **O6** (pyproject.toml schema): Can be decided during development.

### IN_20260510_settings_and_defaults

- **Q7-Q9** (@Example format): Updated — keyword-first with positional shorthand. No mixed form. beehave's @Example takes keyword args matching placeholder names or positional args mapping left-to-right by step text appearance.

## Remaining Items (Decidable During Development)

| ID | Topic | Notes |
|----|-------|-------|
| D1 | Strategy type inference mapping table | `int` → `st.integers()`, `str` → `st.text()`, `bool` → `st.booleans()`, `float` → `st.floats()`. Implementation detail. |
| D2 | `pyproject.toml` schema | Keys: feature_paths, strict, max_examples, infer_strategies. Easy to add iteratively. |
| D3 | `beehave fix` AST manipulation | How to add missing function parameters to existing signatures. Scoped to the fix command. |
| D4 | Vocabulary source for level 4 | What validates step text at adoption level 4. Deferred to after MVP. |
| D5 | `@Background` execution mechanics | Fixture calling convention, return value handling. Can evolve during implementation. |
| D6 | `__beehave_*__` metadata attributes schema | Exact attribute names and formats. Implementation detail. |