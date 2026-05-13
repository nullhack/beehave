# IN_20260510_collection_mechanics — Collection-Time Validation Mechanics & File Structure

> **Status:** COMPLETE
> **Interviewer:** PO
> **Participant(s):** Project Founder
> **Session type:** Domain deep-dive

---

## General

| ID | Question | Answer |
|----|----------|--------|
| Q1 | What is this session about? | Determining the exact mechanisms beehave uses at collection time to validate tests against .feature specifications, the file structure mapping, ID format, and what validation happens at each adoption level. |
| Q2 | What is the overarching design principle? | Convention over configuration. Sensible defaults (feature file location, ID format, file structure) with configuration overrides in `pyproject.toml`. Exact matching for step text — drift IS the enforcement feature. |

## Feature File Location & Configuration

| ID | Question | Answer |
|----|----------|--------|
| Q3 | Where are .feature files located? | Configurable in `pyproject.toml` under beehave configuration. Default: `docs/features/`. |
| Q4 | What tags are allowed on .feature scenarios? | For now, only `@id:<value>` tags. Hypothesis settings tags like `@max-examples:500` are deferred to a later discussion. No other custom tags at this stage. |

## ID Format & Generation

| ID | Question | Answer |
|----|----------|--------|
| Q5 | What is the ID format in .feature files? | `@id:a1b2c3d4` — the `id:` prefix makes it a distinct, parseable tag. This allows other tag types to coexist on a scenario in the future (e.g., `@id:abc123` alongside other configuration tags). |
| Q6 | How are IDs generated? | beehave auto-generates IDs for scenarios that don't have one, and writes the generated ID directly into the .feature file (modifying the file). This ensures every scenario has an ID from the start. |
| Q7 | How do test functions reference IDs? | The test function name includes the ID as a suffix: `test_*_a1b2c3d4` maps to `@id:a1b2c3d4` in the .feature file. beehave extracts the ID suffix from the function name and finds the matching .feature scenario. |

## File Structure: Feature → Rule → Test Module

| ID | Question | Answer |
|----|----------|--------|
| Q8 | How do .feature files map to test modules? | One .feature file per feature. Test modules follow the Rule structure inside the feature: if no Rule is defined, tests go in `<feature_name>/default_test.py`; if Rules are defined, tests go in `<feature_name>/<rule_name>_test.py`. Example: `balance_accounting.feature` → `tests/features/balance_accounting/default_test.py` (no Rules) or `tests/features/balance_accounting/total_calculation_test.py` (with Rule: Total calculation). |
| Q9 | What is the relationship between test modules and strategies? | Each test module corresponds to exactly one Gherkin Rule (or one Feature if no Rules). Strategy variables for that rule's `<placeholders>` live in that test module. No cross-module resolution, no global registry. |
| Q10 | Can one feature directory have multiple .feature files? | Deferred — not decided yet. |

## Step Text Matching

| ID | Question | Answer |
|----|----------|--------|
| Q11 | How does beehave match step text between .feature and Python? | Exact matching. The decorator step text must match the .feature step text character-for-character (after stripping the Gherkin keyword prefix and tokenizing `<placeholder>` variables). Fuzzy matching is explicitly rejected — vocabulary drift is what beehave is designed to catch and report. |
| Q12 | Why not fuzzy matching? | Fuzzy matching would hide the vocabulary drift that beehave is designed to enforce. If a developer writes `a user with an balance <initial>` in the test but `a user with balance <initial>` in the feature, that's a real inconsistency that beehave should flag. The enforcement IS the feature. |

## Strategy Resolution Scope

| ID | Question | Answer |
|----|----------|--------|
| Q13 | Where are strategy variables resolved? | Module-level variables in the test module. `initial = st.integers(min_value=0)` in `total_calculation_test.py` resolves `<initial>` for all tests in that module. No cross-module resolution, no global registry. |
| Q14 | What about inline strategy kwargs on @Given? | Deferred — earlier discussion leaned toward dropping inline kwargs and keeping module-level → auto-infer as the two resolution mechanisms. This simplifies all five decorators to pure structural annotations (only taking a step text string). Final decision pending. |

## Orphan Detection

| ID | Question | Answer |
|----|----------|--------|
| Q15 | What happens when a test has no matching .feature scenario? | Orphan test: a Python test function with an @id suffix that has no matching .feature scenario. Flagged as error (strict mode) or warning (permissive mode). |
| Q16 | What happens when a .feature scenario has no matching test? | Orphan scenario: a .feature scenario with @id that has no matching Python test. Flagged as error (strict mode) or warning (permissive mode). |
| Q17 | When does orphan detection activate? | At adoption level 1 (no .feature file), orphan detection is off. At level 2+ (with .feature files), it activates. |

## Level 1 Validation (No .feature File)

| ID | Question | Answer |
|----|----------|--------|
| Q18 | What does beehave validate at adoption level 1 (no .feature file)? | Two checks: (1) Step ordering — Given must come before When, which must come before Then. @And/@But inherit the ordering of the step type they continue. (2) Placeholder-parameter matching — every `<placeholder>` name in decorator step text must appear as a function parameter. |
| Q19 | What is NOT validated at level 1? | Step text matching against .feature files (no .feature file exists). Vocabulary validation against domain terms (no glossary). @id traceability (no .feature scenarios to trace to). |

## Deferred Decisions

| ID | Topic | Notes |
|----|-------|-------|
| D1 | ID generation format | **Resolved:** Random 8-character IDs, generated once, permanent. Editing scenario text does not change the ID. |
| D2 | @example auto-generation | **Resolved:** `beehave generate` creates @Example decorators from .feature Examples table rows. |
| D3 | Inline strategy kwargs on @Given | **Resolved:** Dropped. All five decorators take only a step text string. Strategy resolution is module-level variables → infer from @Example values → `st.integers()` fallback. |
| D4 | Vocabulary source for level 4 | Whether vocabulary is validated against .feature step text, a glossary, or both. Not yet decided. |
| D5 | Background support | **Resolved:** @Background decorator referencing a fixture function with proper step decorators. All parameters (including background) appear in the test function signature. Multiple scenarios can share the same @Background. |
| D6 | Multiple .feature files per feature directory | **Resolved:** One .feature file per feature, one test directory per feature. 1:1 mapping. |
| D7 | Hypothesis settings tags in .feature | `@max-examples:500` and similar settings tags are deferred. .feature files only have `@id:` tags for now. |

---

## Quality Attributes

| ID | Attribute | Scenario | Target | Priority |
|----|-----------|----------|--------|----------|
| QA1 | Correctness | When a test decorator's step text differs from the .feature step text (after stripping keywords and tokenizing placeholders), beehave must flag the mismatch | Exact character-for-character matching; no fuzzy tolerance; mismatches produce clear error messages | Must |
| QA2 | Auto-configuration | When a .feature scenario has no @id tag, beehave must generate one and write it into the file | Auto-generated IDs are random 8-character values, generated once and permanent; writing must preserve file formatting *(Updated per IN_20260510_adversarial_review R1: resolved from deterministic-or-unique to random permanent.)* | Must |
| QA3 | Progressive validation | When no .feature file exists, beehave must still validate step ordering and placeholder-parameter matching | Level 1 validation must work with zero configuration and no .feature files | Must |

---

## Pain Points Identified

- Without exact step matching, vocabulary drift goes undetected — fuzzy matching would undermine the core value proposition
- Cross-module strategy resolution would create hidden dependencies between test modules, violating the one-module-per-rule principle

## Business Goals Identified

- Enforce vocabulary consistency through exact step matching — any drift between .feature and test is caught at collection time
- Keep the file structure intuitive: one module per rule, strategies scoped to where they're used
- Make auto-ID generation seamless — developers shouldn't have to manually manage IDs

## Terms to Define (for glossary)

- **@id tag** — The `@id:<value>` tag on a Gherkin scenario that links it to a Python test function. Auto-generated by beehave if not present. The `id:` prefix distinguishes it from other potential tag types.
- **Orphan test** — A Python test function whose @id suffix has no matching .feature scenario. Flagged at collection time in strict/permissive mode.
- **Orphan scenario** — A .feature scenario whose @id has no matching Python test function. Flagged at collection time.
- **Exact step matching** — Step text in decorators must match .feature step text character-for-character (after stripping keywords and tokenizing placeholders). No fuzzy matching, no normalization. Vocabulary drift is what beehave catches.

## Updates to Previous INs

### IN_20260510_beehave_design

- **Q8** (Gherkin-to-Hypothesis mapping): Updated — `@max-examples:500` and similar Hypothesis settings tags in .feature files are deferred. Only `@id:` tags are supported initially.
- **Q10** (Strategy resolution): Inline kwargs on @Given being dropped — simplifying to module-level → auto-infer only. All five decorators take only a step text string. Pending final founder confirmation.
- **Q11** (@id format): Updated from `@a1b2c3d4` to `@id:a1b2c3d4` with the `id:` prefix.

### IN_20260510_step_decorator_runtime

- No updates from this session.

## Action Items

- [ ] Decide on ID generation format (short hash, UUID, or human-readable)
- [ ] Decide whether beehave auto-writes @example decorators into test files from .feature Examples tables
- [ ] Confirm dropping inline strategy kwargs on @Given (simplify to module-level → auto-infer)
- [ ] Design vocabulary source for level 4 validation (.feature text, glossary, or both)
- [ ] Design Background support in beehave
- [ ] Decide on multiple .feature files per feature directory
- [ ] Design the `pyproject.toml` configuration schema for beehave (feature file location, strict/permissive mode, etc.)