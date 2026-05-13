# IN_20260511_self_check_round3_pain_points — Self-Check Round 3: 4 Pain Points (PP12-PP15)

> **Status:** COMPLETE
> **Interviewer:** PO
> **Participant(s):** Dogfood Tester / Stakeholder
> **Session type:** Feature specification

---

## General

| ID | Question | Answer |
|----|----------|--------|
| Q1 | What is this session about? | A third self-validation exercise discovered 3 new pain points (PP12-PP14) and a design discussion produced a 4th (PP15). PP12 (And/But not imported) and PP13 (Scenario Outline non-idempotent) are Critical. PP14 (fix escape false positive) is Medium. PP15 (simplified parameterization for plain Scenarios) is a new feature request born from exploring how beehave handles variables. |
| Q2 | What was the exercise? | (1) Write .feature files using And/But steps, Scenario Outline with Examples, and steps containing apostrophes. (2) Run sync → generate → fix cycle. (3) Observe that regular Scenario: blocks are fully idempotent but Scenario Outline expanded rows are not. (4) Explore parameterization design for plain Scenario: blocks. |
| Q3 | What is the reference for expected behavior? | IN_20260511_rich_gherkin_pain_points (PP7-PP11) established Scenario Outline support. The product definition's idempotency quality attribute requires all CLI commands to be idempotent. The stakeholder's parameterization design discussion (see PP15 below) establishes new syntax rules. |
| Q4 | How do these relate to previous pain points? | PP12-PP14 were discovered by exercising the features added in 6a-6d (parser keyword recognition, quote escaping, fix alignment, generate messaging). PP15 is a new design requirement that emerged from the stakeholder asking "how would I declare a simple scenario to capture the variable and value?" — the current limitation forces Scenario Outline + Examples even for single cases. |

## Pain Point: And/But Decorators Not Imported in Generated Stubs

| ID | Question | Answer |
|----|----------|--------|
| PP12-Q1 | What did the tester experience? | Running `beehave generate` on a .feature file with `And` or `But` steps produces stubs that use `@And(...)` and `@But(...)` decorators but only import `Given, When, Then, Example` from `beehave.decorators`. The generated file is a `NameError` at import time — uncollectable by pytest. |
| PP12-Q2 | What is the expected behavior? | Generated stubs should import all decorator types they use. If a step uses `@And` or `@But`, those names must appear in the import line. |
| PP12-Q3 | What is the gap? | `_generate_stub_content()` in `cli.py` has a fixed import line that only includes `Given, When, Then, Example`. The keyword mapping produces `@And` and `@But` decorators correctly but the import block doesn't include them. |
| PP12-Q4 | Fix recommendation? | **Must.** The import line should be dynamically generated based on which decorator types are actually used in the scenario's steps. If any step uses `And`, include it. If any uses `But`, include it. Alternatively, always import all 6 decorator names (Given, When, Then, And, But, Example) since the import cost is negligible and it prevents this class of bug entirely. |

## Pain Point: Scenario Outline Expanded Rows Are Not Idempotent

| ID | Question | Answer |
|----|----------|--------|
| PP13-Q1 | What did the tester experience? | Running `beehave generate` twice on a .feature file containing `Scenario Outline:` with `Examples:` tables appends duplicate test functions on the second run. Each re-parse generates new random @ids for expanded rows, so deduplication fails. |
| PP13-Q2 | What is the expected behavior? | Re-running `beehave generate` should be idempotent — no new test functions appended for existing scenarios. The product definition's idempotency quality attribute mandates this. |
| PP13-Q3 | What is the gap? | `parse_feature()` expands Scenario Outline Examples rows into separate `Scenario` entities, each with a freshly generated `IdTag` via `generate_id()`. Since @ids are random, they differ on each parse. The deduplication check (existing @id in test file) cannot match. |
| PP13-Q4 | Fix recommendation? | **Must.** Derive expanded-row @ids deterministically from the Scenario Outline heading's @id + row index or row content hash. Same rows must always produce the same @ids across parses. This is the same class of issue as idempotency — random IDs violate the product definition's quality attribute. |

## Pain Point: Fix Command False Positive on Escape Sequences

| ID | Question | Answer |
|----|----------|--------|
| PP14-Q1 | What did the tester experience? | The `beehave fix` command reports a text mismatch between `@And('the hive\'s honey stores are replenished')` in the test file and `the hive's honey stores are replenished` in the .feature file. The `\'` is Python's escape for a literal single quote — semantically identical. Fix reports this as a mismatch and applying the "fix" doesn't resolve it, creating an infinite loop. |
| PP14-Q2 | What is the expected behavior? | `beehave fix` should not report a mismatch when the only difference is Python string escaping of quote characters. Semantically identical strings should match. |
| PP14-Q3 | What is the gap? | `_align_steps()` compares decorator text (which includes `\'`) against step text from the .feature file (which has `'`). The comparison is literal string equality without accounting for Python string escaping. |
| PP14-Q4 | Fix recommendation? | **Should.** Unescape Python string escapes in the decorator text before comparison. Use `ast.literal_eval()` or targeted `replace("\\'", "'")` / `replace('\\"', '"')`. The comparison should be on the semantic string value, not the source representation. |

## Pain Point: Plain Scenarios Cannot Be Parameterized Without Scenario Outline Ceremony

| ID | Question | Answer |
|----|----------|--------|
| PP15-Q1 | What did the tester experience? | Writing a simple `Scenario: Simple bee` with `Given a bee named "zoom" when flying` and wanting to parameterize "zoom" and "flying" requires rewriting the entire scenario as `Scenario Outline:` with `<placeholder>` syntax and an `Examples:` table. This is heavyweight for single-row cases and creates friction when evolving a concrete scenario into a parameterized one. |
| PP15-Q2 | What is the expected behavior? | Plain `Scenario:` blocks should support `<placeholder>` syntax for variables. Hypothesis generates values from strategy resolution. The `<placeholder>` syntax is valid Gherkin text — other tools treat it as literal, maintaining compatibility. Examples tables are only valid under `Scenario Outline:`/`Scenario Template:`, not plain `Scenario:`. |
| PP15-Q3 | What is the gap? | `parse_feature()` only recognizes `<placeholder>` patterns in `Scenario Outline:` contexts. Plain `Scenario:` blocks with `<placeholder>` in step text are treated as literal text. The extraction and parameterization logic is gated on the `Scenario Outline:` keyword. |
| PP15-Q4 | Fix recommendation? | **Should.** Allow `<placeholder>` syntax in plain `Scenario:` blocks (not `Scenario Outline:` — that already works). Rules: (1) `<name>` = variable with type from strategy resolution (existing mechanism). (2) `'<name>'` (quoted) = explicitly string type. (3) Hypothesis generates values from strategies. This is a small delta — `parse_feature()` needs to extract placeholders from plain scenarios, and `_generate_stub_content()` needs to detect the `'<name>'` pattern for string type hinting. Gherkin-compatible because `<placeholder>` is valid text in any scenario context. |

---

## Quality Attributes

| ID | Attribute | Scenario | Target | Priority |
|----|-----------|----------|--------|----------|
| QA12 | Import completeness | When generate() creates stubs with And/But decorators, those names are importable | No NameError at import time; pytest can collect the file (fixes PP12) | Must |
| QA13 | Idempotency for Scenario Outline | When generate() is run twice on the same .feature file, no duplicate test functions are created | Same @ids produced for same expanded rows across parses (fixes PP13) | Must |
| QA14 | Escape-aware comparison | When fix() compares decorator text to feature step text, semantically identical strings match | No false mismatch on escaped quotes; fix loop is broken (fixes PP14) | Should |
| QA15 | Universal parameterization | When a plain Scenario: uses <placeholder> syntax, variables are extracted and test stubs are generated with parameters | Stubs have function parameters matching <placeholder> names; Hypothesis strategies resolve by name (enables PP15) | Should |
---

## Pain Points Identified

- **PP12 (Critical)**: And/But decorators used in generated stubs but not imported — `NameError` at import, file uncollectable by pytest. Fixed import line in `_generate_stub_content()` omits these names.
- **PP13 (Critical)**: Scenario Outline expanded rows get new random @ids on each parse — re-running generate appends duplicates. `parse_feature()` generates non-deterministic IDs for expanded rows.
- **PP14 (Medium)**: Fix command reports false mismatch on escaped quotes (`\'` in test vs `'` in .feature). Applying "fix" doesn't resolve it, creating an infinite loop. Literal string comparison without escape awareness.
- **PP15 (Should)**: Plain `Scenario:` blocks cannot use `<placeholder>` syntax for parameterization — requires rewriting as `Scenario Outline:` + `Examples:` table. User wants `<name>` = variable (strategy resolution), `'<name>'` = string type, no Examples = Hypothesis mode.

## Business Goals Identified

- Ensure generated stubs are always importable — a NameError on import means the entire feature file is unusable. All decorator types used in stubs must be imported.
- Guarantee idempotency for all CLI commands — the product definition mandates it. Scenario Outline expanded rows must produce stable, deterministic @ids.
- Make fix command trustworthy — false positives on escape sequences erode developer trust. Semantically identical strings must match.
- Reduce ceremony for parameterized scenarios — allow developers to start with a concrete scenario and evolve it by adding `<placeholder>` syntax, without rewriting as Scenario Outline. Stay Gherkin-compatible.

## Terms to Define (for glossary)

- **Deterministic @id** — An @id derived from stable inputs (scenario heading + row index or content hash) rather than random generation. Produces the same @id across parses, enabling idempotent operations.
- **Escape-aware comparison** — Comparing Python source representations by evaluating string escapes before comparison. `\'` and `'` are semantically identical and should match.
- **Universal parameterization** — The ability to use `<placeholder>` syntax in any scenario type (Scenario: or Scenario Outline:), not just Scenario Outline. Variables are resolved via strategy resolution; quoted placeholders force string type.
- **Strategy resolution** — Mapping a `<placeholder>` name to a Hypothesis strategy by looking up a module-level variable with the same name. If not found, falls back to `st.integers()` with a UserWarning.

## Architecture Decisions

### AD4 — PP13: Deterministic @id generation for expanded rows

**Decision:** Derive expanded-row @ids from `hash(scenario_heading_id + str(row_index))` truncated to 8 hex characters.

**Rationale:** The scenario heading already has a stable @id (assigned by sync). The row index within the Examples table is deterministic (order-preserving). Combining them produces a unique, stable @id for each expanded row. Using `hash()` + truncation avoids the need for a new ID generation mechanism — it reuses the existing `IdTag` format but derives the value instead of randomizing it.

**Risk:** If the Examples table rows are reordered, the @ids change. This is acceptable because row reordering is a semantic change — the test functions would need regeneration anyway. If the scenario heading's @id changes (re-sync), all expanded rows change too — consistent and expected.

---

### AD5 — PP15: Universal parameterization via `<placeholder>` in any scenario type

**Decision:** Allow `<placeholder>` syntax in plain `Scenario:` blocks (not Scenario Outline — that already works). Extract placeholders and generate test functions with parameters. Detection rules:
- `<name>` → variable, type from strategy resolution
- `'<name>'` → variable, explicitly string type (overrides strategy resolution)
- Hypothesis generates values from strategies
- Examples tables are only valid under Scenario Outline/Template, not plain Scenario

**Rationale:** This is a minimal extension to existing mechanisms. `parse_feature()` already extracts `<placeholder>` patterns via regex — it just needs to do this for all scenario types, not only Scenario Outlines. `_generate_stub_content()` already produces function parameters from placeholders. The `'<name>'` quoted pattern is a new detection rule that forces string type, which can be implemented as a simple regex check. Strategy resolution is already built (module-level variable lookup + `st.integers()` fallback). The .feature file remains Gherkin-compatible — `<placeholder>` is valid text in any scenario context, and other BDD tools treat it as a literal string.

**Risk:** Other BDD tools won't substitute `<placeholder>` in plain Scenario: blocks — they'll treat it as literal text. This is acceptable because beehave's parameterization is a beehave-specific feature; the .feature file doesn't break for other tools. The quoted `'<name>'` pattern is a beehave convention that adds a type hint — it's optional and doesn't affect Gherkin parsing.

---

## Action Items

- [ ] Fix PP12: Dynamically generate import line in `_generate_stub_content()` based on decorator types used, or always import all 6 names
- [ ] Fix PP13: Derive expanded-row @ids deterministically from heading @id + row index in `parse_feature()`
- [ ] Fix PP14: Unescape Python string escapes in decorator text before comparison in `_align_steps()`
- [ ] Implement PP15: Allow `<placeholder>` in plain `Scenario:` steps; detect `'<name>'` for string type; generate parameters without requiring Scenario Outline
- [ ] Create feature files for 7a (PP15), 7b (PP12), 7c (PP13), 7d (PP14)
- [ ] Verify PP12 and PP13 fixes don't interact (separate code paths: imports vs. @id generation)
- [ ] Verify PP15 integrates cleanly with existing Scenario Outline expansion (no double-parameterization)
