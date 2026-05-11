# IN_20260511_rich_gherkin_pain_points — Rich Gherkin Re-Exercise: 5 Pain Points with Scenario Outline, Quotes, Step Boundaries, Fix Diffing, and Missing @id Guidance

> **Status:** COMPLETE
> **Interviewer:** PO
> **Participant(s):** Dogfood Tester
> **Session type:** Feature specification

---

## General

| ID | Question | Answer |
|----|----------|--------|
| Q1 | What is this session about? | A second self-validation exercise using richer Gherkin constructs (Background:, Scenario Outline: + Examples: tables, Rule: blocks, And/But chaining). Five new pain points were discovered beyond the 6 already fixed in the self_validation_fixes feature (PP1–PP6 from IN_20260511_self_validation_pain_points). This session extracts the new pain points into structured interview notes for prioritization and action. |
| Q2 | What was the exercise? | (1) Write `docs/features/hive_inspection.feature` with `Scenario Outline:`, `Examples:` tables, quoted values in step text, consecutive scenarios of different types, mid-scenario step insertions, and scenarios without `@id` tags. (2) Run `beehave sync` to assign @id tags. (3) Run `beehave generate` to create stubs. (4) Run `beehave fix --dry-run` after mutating the .feature file. (5) Attempt to run `pytest` on generated output. |
| Q3 | What is the reference for expected behavior? | The Gherkin-6 official specification defines `Scenario Outline:` and `Scenario Template:` as valid aliases. IN_20260510_cli_commands defines the generate/fix/sync contracts. The project's own TDD convention and existing feature files define expected stub behavior. PP1–PP6 fixes (from the self_validation_fixes feature) are assumed applied. |
| Q4 | How do these relate to the previous pain points? | PP1–PP6 (empty file paths, repeated imports, missing __init__.py, silent-pass stubs, omitted step decorators, strategy fallback silence) were discovered with basic Gherkin and are already fixed. PP7–PP11 were only discoverable with richer Gherkin constructs — they are deeper parser and logic bugs that basic scenarios never surface. |

## Pain Point: Scenario Outline/Template Not Recognized by Parser

| ID | Question | Answer |
|----|----------|--------|
| PP7-Q1 | What did the tester experience? | Writing a `Scenario Outline: Varroa mite count assessment` with 4 `Examples:` rows and running `sync()` then `generate()` produced nothing — no `@id` tags assigned, no stubs generated, no warnings emitted. The entire scenario outline was invisible to the parser. |
| PP7-Q2 | What is the expected behavior? | The parser should recognize `Scenario Outline:` and `Scenario Template:` as valid Gherkin-6 scenario headings. Each row in the `Examples:` table should be expanded into its own `Scenario` with `<placeholder>` values substituted, each receiving its own `@id` tag. |
| PP7-Q3 | What is the gap? | `_is_scenario_heading()` in `traceability.py:148-149` only matches lines starting with `Example:` or `Scenario:` — it does not match `Scenario Outline:` or `Scenario Template:`. These are official Gherkin keywords that are simply missing from the recognition list. (Source: PM_20260511_scenario_outline_ignored) |
| PP7-Q4 | Fix recommendation? | **Must.** Extend `_is_scenario_heading()` to match `Scenario Outline:` and `Scenario Template:`. When found, expand into one `Scenario` per row in the `Examples:` table with placeholder substitution. Each expanded row gets its own `@id`. Add tests for both keyword aliases and multi-row expansion. Without this, any feature file using `Scenario Outline:` — one of the most common Gherkin patterns — is completely unusable. |

## Pain Point: Unescaped Quotes in Generated Decorator Strings

| ID | Question | Answer |
|----|----------|--------|
| PP8-Q1 | What did the tester experience? | Generated file `tests/features/hive_inspection/default_test.py` contained `@Given("hive "Alpha" has 10 frames of bees")` — nested double quotes produce `SyntaxError: invalid syntax`. The file could not be imported by pytest at all. |
| PP8-Q2 | What is the expected behavior? | Generated Python code must be syntactically valid. When step text contains quotes, the generator must use an escaping strategy (alternate quote character, backslash escaping, or triple-quoted strings) so the resulting decorator is valid Python. |
| PP8-Q3 | What is the gap? | `_generate_stub_content()` in `cli.py:270-271` writes step decorators as `f'@{keyword}("{step_text}")'` without escaping any characters in `step_text`. When Gherkin step text contains double quotes (e.g., `hive "Alpha"`), the generated Python string literal breaks. (Source: PM_20260511_unescaped_quotes_in_stubs) |
| PP8-Q4 | Fix recommendation? | **Must.** In `_generate_stub_content()`, detect if `step_text` contains the chosen quote character and switch to the alternate quote, or escape inner quotes. Recommended approach: always use single quotes for the outer decorator string and escape any single quotes in the step text. Add a test that generates stubs from a feature with quoted values and verifies the output passes `py_compile.compile()`. A generated file that won't import is a total showstopper. |

## Pain Point: Steps Leak Across Scenario Boundaries When Scenario Outline Follows

| ID | Question | Answer |
|----|----------|--------|
| PP9-Q1 | What did the tester experience? | `@id:6399af56` ("Disease detected during inspection") received 4 extra step decorators from the `Scenario Outline: Varroa mite count assessment` that follows it. The generated test function `test_disease_detected_during_inspection_6399af56` incorrectly had `@Given("hive "<hive_name>" has a Varroa mite count...")` and 3 more Varroa steps appended after its own correct steps. |
| PP9-Q2 | What is the expected behavior? | Steps must be scoped to their own scenario. `_parse_feature_steps()` must stop collecting steps at any scenario boundary — including `Scenario Outline:` and `Scenario Template:`. Each scenario's test function must contain only its own step decorators. |
| PP9-Q3 | What is the gap? | `_is_section_break()` in `traceability.py:156-157` only checks for `Example:`, `Scenario:`, `Rule:`, and `Feature:`. Since `Scenario Outline:` is not in `_SECTION_BREAK_KEYWORDS`, the parser never stops collecting steps — it continues through the `Scenario Outline:` heading and collects all its steps too. This is the same root cause as PP7 (missing keyword recognition) but manifests as a data corruption bug: existing scenarios receive foreign steps. (Source: PM_20260511_step_leakage_across_scenarios) |
| PP9-Q4 | Fix recommendation? | **Must.** Add `"Scenario Outline:"` and `"Scenario Template:"` to `_SECTION_BREAK_KEYWORDS`. Better: make the section break check prefix-based — any line starting with `Scenario` or `Example` should be a section break, which is resilient to future keyword additions. Add a test where `Scenario Outline:` follows a `Scenario:` and verify steps don't leak. ARCHITECTURE QUESTION: Should `_is_section_break()` be refactored to prefix-based matching as a general solution, or should keyword lists be the canonical approach for maintainability and explicitness? This affects the parsing architecture. |

## Pain Point: Fix Command Misinterprets Step Insertion as Text Replacement Cascade

| ID | Question | Answer |
|----|----------|--------|
| PP10-Q1 | What did the tester experience? | After inserting a new step "And hive 'Lambda' was inspected within the last 7 days" between existing steps in a scenario, `fix --dry-run` proposed replacing 4 existing decorator texts by shifting them all one position — instead of inserting the new decorator and keeping existing ones unchanged. The fix command treated one insertion as four modifications. |
| PP10-Q2 | What is the expected behavior? | The fix command should recognize that existing decorators still match feature steps (just at a different offset) and propose a single insertion, not a cascade of text replacements. A developer inserting one step should see one proposed change, not N. |
| PP10-Q3 | What is the gap? | `_find_text_mismatches()` in `cli.py:520-546` compares feature steps and test decorators position-by-position (index `i` in both lists). It has no concept of diffing — it cannot distinguish "text changed at position N" from "text inserted at position N, shifting all subsequent". When a step is inserted, every position after it is a mismatch. (Source: PM_20260511_fix_step_insertion_misalignment) |
| PP10-Q4 | Fix recommendation? | **Should.** Use a proper diff algorithm (Longest Common Subsequence or similar) to match feature steps to existing decorators by content similarity, not just position. At minimum, detect the pattern where N consecutive decorators match N feature steps at offset +1 and treat it as a single insertion. Add test for mid-scenario step insertion. ARCHITECTURE QUESTION: Is LCS the right algorithm here, or should we use a simpler heuristic (e.g., "find longest matching suffix/prefix")? The complexity of the diff affects both correctness and maintainability. This needs SA input on the tradeoffs. |

## Pain Point: generate() Silently Skips Scenarios Without @id Tags With No Guidance

| ID | Question | Answer |
|----|----------|--------|
| PP11-Q1 | What did the tester experience? | After writing 3 `Scenario:` blocks without `@id` tags and running `generate()`, the output said "no scenarios found" despite 3 scenarios clearly existing in the file. No guidance was given about needing to run `sync()` first. The developer experience was: write `.feature` → run `generate()` → "no scenarios found" → confusion. |
| PP11-Q2 | What is the expected behavior? | `generate()` should distinguish between "file has no scenarios at all" and "file has N scenarios but none have @id tags". The latter should produce an actionable message like "3 scenarios found without @id tags. Run `beehave sync` to assign IDs, then re-run generate." Optionally, `generate()` could auto-detect and run `sync()` or prompt the developer. |
| PP11-Q3 | What is the gap? | `generate()` in `cli.py:46` filters to only scenarios with `id_tag is not None`. If none have `@id` tags, the list is empty and the result is `{action: "skipped", reason: "no scenarios found"}`. The message "no scenarios found" is misleading — scenarios were found, they just don't have `@id` tags. (Source: PM_20260511_generate_silent_skip_no_id) |
| PP11-Q4 | Fix recommendation? | **Should.** Change the "no scenarios found" message to distinguish the two cases. Better: auto-detect scenarios without `@id` tags and return a clear actionable message. ARCHITECTURE QUESTION: Should `generate()` auto-invoke `sync()` when it detects untagged scenarios, or should it only advise? Auto-invocation is more convenient but violates the single-responsibility principle of the CLI commands. This is a UX vs. architectural cleanliness tradeoff that needs stakeholder input. |

---

## Quality Attributes

| ID | Attribute | Scenario | Target | Priority |
|----|-----------|----------|--------|----------|
| QA7 | Parser completeness | When a .feature file uses `Scenario Outline:` or `Scenario Template:`, the parser recognizes and expands it | Each Examples: row produces a separate scenario with its own @id (fixes PP7) | Must |
| QA8 | Generated code validity | When step text contains quotes, the generated decorator is valid Python | All generated files pass `py_compile.compile()` (fixes PP8) | Must |
| QA9 | Step boundary integrity | When scenarios of different types are adjacent, steps do not leak across boundaries | Each scenario's test function contains only its own step decorators (fixes PP9) | Must |
| QA10 | Fix accuracy | When a step is inserted mid-scenario, fix proposes a single insertion | fix --dry-run shows 1 insertion, not N replacements (fixes PP10) | Should |
| QA11 | Developer guidance | When generate() is run on untagged scenarios, the developer is told what to do | Output says "N scenarios found without @id tags — run sync first" (fixes PP11) | Should |

---

## Pain Points Identified

- **PP7 (Critical)**: `Scenario Outline:` / `Scenario Template:` not recognized by `_is_scenario_heading()` — these Gherkin-6 keywords are missing from the parser's recognition list, making entire scenario outlines invisible to sync/generate.
- **PP8 (Critical)**: Generated decorator strings contain unescaped quotes — `_generate_stub_content()` uses `f'@{keyword}("{step_text}")'` without escaping, producing `SyntaxError` when step text contains double quotes. Generated files cannot be imported.
- **PP9 (Critical)**: Steps leak across scenario boundaries — `_is_section_break()` does not include `Scenario Outline:` / `Scenario Template:`, so `_parse_feature_steps()` never stops collecting steps and subsequent scenario outlines' steps are appended to the preceding scenario's test function.
- **PP10 (High)**: Fix command uses positional comparison instead of diff — when a step is inserted mid-scenario, `_find_text_mismatches()` sees every subsequent position as changed, proposing N text replacements instead of 1 insertion.
- **PP11 (Medium)**: `generate()` silently skips scenarios without `@id` tags with the misleading message "no scenarios found" — no guidance to run `sync()` first. New users hit this immediately on first use.

## Business Goals Identified

- Ensure the parser handles the full Gherkin-6 keyword set — `Scenario Outline:` and `Scenario Template:` are fundamental Gherkin constructs used pervasively in real-world feature files. Without support, beehave cannot handle any feature file using parameterized scenarios.
- Guarantee generated code is always valid Python — a code generator that produces syntax errors destroys trust immediately. Quote escaping is a non-negotiable correctness requirement.
- Prevent data corruption in generated test stubs — step leakage across scenario boundaries means tests assert the wrong things silently. This is worse than no tests at all.
- Make the fix command trustworthy — if fix proposes N changes for a 1-step insertion, developers will stop trusting it and make manual edits, defeating the purpose of the tool.
- Provide actionable guidance at every failure point — "no scenarios found" when 3 scenarios exist is actively misleading. The CLI must tell developers what to do, not hide the problem.

## Terms to Define (for glossary)

- **Scenario Outline** — A Gherkin-6 keyword (alias: `Scenario Template:`) that defines a scenario template with `<placeholder>` values, expanded once per row in the `Examples:` table. Each expansion is a separate test case.
- **Section break** — A parser boundary marker that stops step collection for the current scenario. Defined in `_is_section_break()` as a set of keywords (`Scenario:`, `Example:`, `Rule:`, `Feature:`). Missing keywords cause step leakage.
- **Positional diff** — Comparing two lists element-by-element at the same index. Fails to detect insertions or deletions because it cannot distinguish "text changed" from "text shifted". A proper diff algorithm (e.g., LCS) matches by content similarity instead.
- **Quote escaping** — Replacing or alternating quote characters in generated Python string literals to prevent syntax errors when the embedded text contains the same quote character used as the string delimiter.

## Architecture Decisions

### AD1 — PP9: Section break strategy (prefix-based vs. explicit keyword lists)

**Decision:** Unify on prefix-based matching for both `_is_scenario_heading()` and `_is_section_break()`, using the canonical Gherkin heading prefixes `"Scenario"` and `"Example"`.

**Rationale:** `_is_section_break()` in `traceability.py:156-157` already uses prefix matching — `_SECTION_BREAK_KEYWORDS = ("Example", "Scenario", "Rule", "Feature")` are checked via `startswith`, so `"Scenario Outline:"` already matches. However, `_is_scenario_heading()` at line 148-149 uses explicit colon-terminated matching (`startswith("Example:")` / `startswith("Scenario:")`), which is unnecessarily restrictive. The fix is to align `_is_scenario_heading()` with `_is_section_break()`'s approach: check `stripped.startswith("Scenario") or stripped.startswith("Example")`. This covers all current and future Gherkin keyword variants (`Scenario Outline:`, `Scenario Template:`, `Example:`) without maintaining an explicit keyword list. A secondary concern: `_parse_feature_steps()` in `cli.py:323-342` has no section-break logic at all — it never resets `current_id` when a new scenario heading appears, which is the true root cause of step leakage. It must import and call `_is_section_break()` to reset `current_id = None` at scenario boundaries.

**Risk:** Prefix matching is broader — a line like `"Scenario planning notes"` could be falsely detected. Mitigation: in practice, Gherkin files are structured and such false positives are unlikely. If needed, a stricter check could require the prefix to be followed by a space or colon: `re.match(r'^(Scenario|Example)(\s|:)', stripped)`.

---

### AD2 — PP10: Diff algorithm selection for fix command

**Decision:** Use Python's `difflib.SequenceMatcher` (stdlib) for step-to-decorator alignment in `_find_text_mismatches()`, replacing the current positional comparison.

**Rationale:** The current implementation at `cli.py:533` iterates `enumerate(steps)` and compares `decorators[i]` positionally — a single insertion at position N produces mismatches at every subsequent position. A hand-rolled LCS would be correct but adds maintenance burden for an algorithm that's tricky to get right. `difflib.SequenceMatcher` is in the standard library, implements a well-tested Ratcliff/Obershelp algorithm (longest matching subsequence), and returns `get_opcodes()` that directly classify each element as `equal`, `replace`, `insert`, or `delete`. For the typical scenario of 3–10 steps, performance is a non-issue. The code is simpler than either a hand-rolled LCS or a custom heuristic, and produces correct results for insertions, deletions, text changes, and reorderings. A simpler suffix/prefix heuristic would only handle insertions at the beginning or end of the step list, missing mid-sequence insertions entirely — which is exactly the reported pain point.

**Risk:** `SequenceMatcher` uses a "junk" heuristic that can produce unexpected alignments for very similar step texts (e.g., `"Given a hive with 10 frames"` vs `"Given a hive with 20 frames"`). Mitigation: set `autojunk=False` to disable this heuristic, ensuring pure longest-match behavior. Also, `SequenceMatcher` is O(n²) in the worst case, but with typical step counts under 20, this is negligible.

---

### AD3 — PP11: Auto-sync on generate vs. advise only

**Decision:** `generate()` should advise only — detect untagged scenarios and return a clear, actionable message, but never auto-invoke `sync()`.

**Rationale:** `generate()` creates test stubs (writes to `tests/`); `sync()` assigns `@id` tags (mutates `.feature` files). These are separate concerns with separate side effects. Auto-invoking sync from generate violates single-responsibility and the principle of least surprise — a user running `generate` expects test files to be created, not `.feature` files to be modified. The fix is trivial at `cli.py:46-56`: count total scenarios before filtering by `id_tag is not None`, then branch the message. If `scenarios` is non-empty but `orphans` is empty, the message should be `"N scenarios found without @id tags. Run 'beehave sync' first, then re-run generate."` rather than `"no scenarios found"`. Users who want combined behavior can compose: `beehave sync && beehave generate`. The CLI should be composable, not magical.

**Risk:** Advising without acting means an extra manual step for the user. However, the alternative (auto-sync) risks silently mutating `.feature` files the user didn't expect to change — particularly dangerous in CI pipelines or when feature files are version-controlled and the user is experimenting. The advisory approach is safer and more predictable.

---

## Action Items

- [ ] Fix PP7: Extend `_is_scenario_heading()` to match `Scenario Outline:` and `Scenario Template:` — add expansion logic for `Examples:` rows — add tests for both aliases
- [ ] Fix PP8: Add quote escaping to `_generate_stub_content()` — use single quotes for outer string or escape inner quotes — add test with quoted step text that verifies `py_compile.compile()` passes
- [ ] Fix PP9: Align `_is_scenario_heading()` with prefix-based matching (per AD1) — add section-break reset logic to `_parse_feature_steps()` in cli.py — add test with consecutive scenario types verifying no step leakage
- [ ] Fix PP10: Replace positional comparison in `_find_text_mismatches()` with `difflib.SequenceMatcher` (per AD2) — use `get_opcodes()` to classify equal/replace/insert/delete — add test for mid-scenario step insertion
- [ ] Fix PP11: Change "no scenarios found" message to distinguish untagged scenarios from absent scenarios (per AD3) — advise running sync, do not auto-invoke — add test for generate() on feature without @id tags
- [ ] ~~ARCHITECTURE QUESTION (PP9): Route to SA — should `_is_section_break()` use prefix-based matching or explicit keyword lists?~~ → Answered in AD1
- [ ] ~~ARCHITECTURE QUESTION (PP10): Route to SA — is LCS the right diff algorithm for fix, or should we use a simpler heuristic?~~ → Answered in AD2
- [ ] ~~ARCHITECTURE QUESTION (PP11): Route to SA/stakeholder — should `generate()` auto-invoke `sync()` for untagged scenarios, or only advise?~~ → Answered in AD3
- [ ] Prioritize fixes: PP7 + PP8 + PP9 are Must (Critical) — PP10 and PP11 are Should (High/Medium)
- [ ] Verify PP7 and PP9 share a root cause (missing `Scenario Outline:` keyword recognition) — fixes may be coupled
