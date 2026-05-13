# beehave v2 Spec Post-Mortem — Round 7 (Adversarial Pipeline)

> Adversarial emulation targeting areas NOT covered by R1-R6: Unicode title
> normalization, strategy inference edge cases, decorator stacking order,
> cross-module @Background, boolean case sensitivity, and Gherkin parsing
> edge cases. Each issue was validated by implementing the spec literally
> and finding where it breaks.
> All artifacts in `/tmp/beehave-v2-r7/`.

---

## PP-V2-R7-01: Unicode normalization creates duplicate function names ⬇️ DROPPED

**Severity:** High
**Location:** Title format rule (line 15), Collection-Time Check

Title `'ﬁnance report'` (with ﬁ ligature U+FB01) produces function `test_ﬁnance_report`, while `'finance report'` produces `test_finance_report`. These are visually identical but different codepoints. NFKC normalization would make them collide. The spec restricts titles to "Unicode letters, digits, and spaces" — the ligature ﬁ (U+FB01) is category Ll (Lowercase Letter), so it passes validation.

**Dropped:** This is a theoretical edge case. Python identifiers preserve the original codepoints — `ﬁnance` and `finance` are different identifiers. The spec's global uniqueness check compares titles as-is (not normalized). NFKC normalization would be a breaking change for legitimate use of Unicode ligatures in non-English text. The current behavior (different codepoints = different titles = different function names) is correct.

---

## PP-V2-R7-13: outline_random_examples=0 contradicts unconditional @given() wrapping ✅ RESOLVED

**Severity:** High
**Location:** Hypothesis Binding (line 105-129), Configuration (line 320-324)

The spec says `@given()` is applied when ANY step has `<placeholders>` (line 109). But `outline_random_examples=0` means "no random exploration." These are contradictory: Hypothesis `@given()` ALWAYS generates random cases unless `settings(max_examples=0)` or similar is configured. The spec doesn't explain HOW `outline_random_examples=0` is implemented.

**Resolution:** When `outline_random_examples=0`, beehave applies Hypothesis `@given()` with `settings(max_examples=0)`, which causes Hypothesis to run only explicit `@example()` cases and no random cases. When `outline_random_examples=N` (N > 0), beehave applies `@given()` with `settings(max_examples=N)` (in addition to the `@example()` cases, which always run). This is a Hypothesis-level configuration applied by the decorator resolution phase.

**Spec change applied:** Hypothesis Binding section — added `outline_random_examples` / `max_examples` clarification to the "Has `<placeholders>`" bullet.

---

## PP-V2-R7-26: fix command can't update @Background function defined in different module ⬇️ DROPPED

**Severity:** High
**Location:** Fix Command (line 470-472), Architecture

The spec says fix updates `@Background` function step decorators (R6-20 resolution). But if the `@Background` function is imported from another module (e.g., `conftest/bank_backgrounds.py`), fix needs to find and edit that file. The function's `__module__` attribute provides the module name, but resolving module → file path is non-trivial.

**Dropped:** `fix` operates on files it can locate via `inspect.getfile(func)`. If the background function is in a different module, `fix` resolves the source file and edits it. This works for normal Python modules (not zip imports, namespace packages, or REPL-defined functions — all of which are outside beehave's scope). The `fix` command already requires a name argument that resolves to a feature file; background function resolution follows standard Python introspection. No spec change needed — the existing wording ("updates decorator text in scope") covers cross-module backgrounds when the function object is reachable.

---

## PP-V2-R7-01a: Full-width digits produce different function names than ASCII ⬇️ DROPPED

**Severity:** Medium
**Location:** Title format rule (line 15)

Title `'test ２nd attempt'` (full-width ２ U+FF12) → `test_test_２nd_attempt`. Title `'test 2nd attempt'` (ASCII 2) → `test_test_2nd_attempt`. Both are valid Unicode digits (category Nd) but produce different Python identifiers. Python allows non-ASCII identifiers natively.

**Dropped:** Full-width digits are valid Unicode digits. Python distinguishes them from ASCII digits in identifiers. The spec allows Unicode digits, and the function names are genuinely different. If a user writes full-width digits, they get a different function — this is correct and expected.

---

## PP-V2-R7-02: Examples value 'None' treated as string, not Python None ⬇️ DROPPED

**Severity:** Medium
**Location:** Examples table type inference (line 200-228)

If a user writes `'None'` in an Examples cell, type inference treats it as a string (`st.text()`). The generated `@Example(val='None')` passes a string, not Python None.

**Dropped:** This is correct behavior. Gherkin Examples tables contain text, not Python expressions. `'None'` is the text string "None". There is no Gherkin syntax for Python None, nor should there be — beehave does not execute step definitions. Users who need None can define a strategy: `val = st.none()`.

---

## PP-V2-R7-03: @Example/@given stacking order — user writes one, Hypothesis needs another ✅ RESOLVED

**Severity:** Medium
**Location:** Decorator Resolution (line 137-144)

The spec shows user-facing order: `@Given`, `@When`, `@Then`, `@Example`, `def`. But Hypothesis requires `@given()` to be innermost (applied first). The spec says "Wrap with `@hypothesis.example(**values)` in the correct Hypothesis stacking order" (line 142) but never defines what that order is.

**Resolution:** The decorator resolution phase transforms user-facing decorator order into Hypothesis stacking order. The "correct Hypothesis stacking order" is: `@hypothesis.example()` decorators outermost (applied last), `@hypothesis.given()` innermost (applied first), function innermost. This is the only order Hypothesis accepts.

**Spec change applied:** Decorator Resolution step 4 — replaced "in the correct Hypothesis stacking order" with explicit "@example() outermost, @given() innermost (Hypothesis requirement)".

---

## PP-V2-R7-04: Same placeholder name, different inference across features in one file ⬇️ DROPPED

**Severity:** Medium
**Location:** Strategy Inference (line 189-232), generate command

If two scenarios from different features are in the same test file and one has `<count>` inferred as `st.integers()` while the other has `'<count>'` inferred as `st.text()`, the module-level override applies to both.

**Dropped:** The spec routes generated test files per-feature (`tests/features/<feature_name>/default_test.py`). Scenarios from different features are in different files by default. If a user manually combines them, module-level override scoping (line 232: "split the tests into separate files") already documents the solution. No spec change needed.

---

## PP-V2-R7-05: Background function with @And/@But only (no @Given/@When/@Then) ✅ RESOLVED

**Severity:** Medium
**Location:** Background (line 93-103), @And/@But inheritance (line 44)

A background function decorated only with `@And`/`@But` (no `@Given`/`@When`/`@Then`) has no preceding step type to inherit → collection-time error. The spec doesn't explicitly mention this for background functions.

**Resolution:** The `@And`/`@But` inheritance rule (line 44) already covers this: "If `@And` or `@But` appears before any `@Given`/`@When`/`@Then` → collection-time error." This applies to background functions too — they are functions with step decorators.

**Spec change applied:** Background rule 2 — added "The function must start with a `@Given`, `@When`, or `@Then` (not `@And`/`@But`), consistent with Gherkin's requirement that Background steps begin with Given/When/Then."

---

## PP-V2-R7-06: Body enforcement flags unreferenced Then placeholders even with Examples ⬇️ DROPPED

**Severity:** Medium
**Location:** Body Enforcement (line 329-365), Parameter Binding

A Scenario Outline with `<remaining>` in a Then step may not reference `remaining` in the body if the user writes `assert initial - amount == 70` (hardcoded expected value).

**Dropped:** This is correct enforcement behavior. If the user hardcodes the expected value instead of referencing the parameter, they're not actually testing the Examples value. The parameter exists for a reason — body enforcement ensures the test uses it. The fix is straightforward: `remaining = initial - amount; assert remaining == expected_remaining`. This is by design.

---

## PP-V2-R7-07: Gherkin comments (#) inside Examples tables ✅ RESOLVED

**Severity:** Medium
**Location:** Traceability parser, Examples table parsing

Standard Gherkin allows `#` comments. If a `#` comment line appears between Examples rows, or inside a cell value, the spec doesn't define parser behavior.

**Resolution:** The parser follows standard Gherkin convention: `#` at the start of a line (outside table cells) is a comment line and is ignored. Inside table cells (between `|` delimiters), `#` is literal text. This is the behavior of all major Gherkin implementations (Cucumber, Behave, SpecFlow).

**Spec change applied:** `beehave.traceability` architecture section — added "Lines starting with `#` (outside table cells) are comments and ignored. Inside table cells, `#` is literal text."

---

## PP-V2-R7-14: @Example bijection — tuple vs list mismatch for same values ✅ RESOLVED

**Severity:** Medium
**Location:** Collection-Time Check (line 460), Examples type inference

If the Examples table has `[1, 2]` (inferred as list), the cache stores `[1, 2]`. If the user writes `@Example(val=(1, 2))` (a tuple), bijection comparison uses `==` which returns `False` for `[1, 2] == (1, 2)`.

**Resolution:** The `generate` command always produces Python lists for Gherkin list syntax, matching the inferred type. If a user manually changes `[]` to `()` in `@Example`, the bijection fails — this is correct behavior. The user should keep the generated type.

**Spec change applied:** Collection-Time Check step 6 — added "`@Example` values must match the inferred type exactly — lists in Gherkin remain lists in Python, not tuples."

---

## PP-V2-R7-15: UTF-8 BOM breaks feature file parsing ✅ RESOLVED

**Severity:** Medium
**Location:** Traceability parser

Feature files saved with UTF-8 BOM (U+FEFF) would have an invisible character before `Feature:`, causing the parser to fail.

**Resolution:** The parser reads feature files with `encoding='utf-8-sig'`, which transparently strips UTF-8 BOM. This is standard Python practice.

**Spec change applied:** `beehave.traceability` architecture section — added "Feature files are read as UTF-8 (transparently handles UTF-8 BOM)".

---

## PP-V2-R7-17: @Example on no-placeholder function — undefined behavior ✅ RESOLVED

**Severity:** Medium
**Location:** Hypothesis Binding (line 105-129), @Example (line 535)

If a user adds `@Example` to a function with no `<placeholders>`, there's no `@given()` wrapping. Hypothesis `@example()` without `@given()` is invalid.

**Resolution:** Collection-time error: `@Example found on function with no placeholders. @Example requires @given(), which is only applied when placeholders exist. Remove @Example or add <placeholders> to step text.`

**Spec change applied:** `@Example` description in Architecture — added "`@Example` is only valid on functions with `<placeholders>` in step text (which triggers `@given()` wrapping). `@Example` on a no-placeholder function → collection-time error."

---

## PP-V2-R7-20: Boolean inference case-sensitive — 'True'/'FALSE' inferred as st.text() ✅ RESOLVED

**Severity:** Medium
**Location:** Examples table type inference (line 209-228)

The spec says `'true'`, `'false'` → `st.booleans()`. But Python booleans are `'True'`/`'False'` (capitalized). Users writing `'True'` in Examples would get `st.text()` instead of `st.booleans()`.

**Resolution:** Boolean detection is case-insensitive. Any casing of `true`/`false` (`True`, `TRUE`, `true`, `False`, `FALSE`, `false`) infers `st.booleans()`.

**Spec change applied:** Examples table type inference — updated boolean row to show all casings and added "(case-insensitive)".

---

## PP-V2-R7-22: Multiple @Background order — reversed order breaks vocabulary enforcement ✅ RESOLVED

**Severity:** Medium
**Location:** Background (line 93-103), Collection-Time Check (line 457)

If the user reverses `@Background` decorators (`@Background(rule_bg)` before `@Background(feature_bg)`), the combined step list would have rule background before feature background, but the cache expects feature-first.

**Resolution:** `@Background` decorators must be in feature → rule order (matching the cache structure). Reversed order → collection-time error.

**Spec change applied:** Background rule 5 — added "Multiple `@Background` decorators must be in hierarchical order: feature background first, rule background second. Reversed order → collection-time error."

---

## PP-V2-R7-27: Placeholder named after Python builtin shadows it in function body ✅ RESOLVED

**Severity:** Medium
**Location:** Placeholder Syntax (line 150)

Placeholder names like `<list>`, `<dict>`, `<str>` pass validation (not keywords, are valid identifiers). But the generated function `def test_...(list): ...` shadows the builtin `list()`.

**Resolution:** The parser rejects placeholder names that match Python builtins. Parse error: `"Placeholder '<list>' shadows Python builtin. Choose a different name."` Checked against all names in the `builtins` module.

**Spec change applied:** Placeholder Syntax — updated from "valid Python identifiers and not Python keywords" to "valid Python identifiers, not Python keywords, and not Python builtins (names in the `builtins` module)".

---

## PP-V2-R7-02a: Whitespace-only Examples cell: trim or preserve? ⬇️ DROPPED

**Severity:** Low
**Location:** Examples table type inference (line 228)

Whitespace-only cells: trim to empty string or preserve?

**Dropped:** Gherkin table cells have their leading/trailing whitespace stripped by convention (all major implementations). Whitespace-only cells become empty strings. `st.text()` inference is correct. No spec change needed.

---

## PP-V2-R7-08: Generate idempotency — matching criteria undefined ⬇️ DROPPED

**Severity:** Low
**Location:** generate command (line 488-512)

The spec says generate creates stubs "for each scenario without a matching test function" but doesn't define the matching criteria precisely.

**Dropped:** The matching is by function name (derived from scenario title) existence in the target test file. This is implied by the spec's function name derivation rules (line 417). Generate reads the test file, checks if the function exists, and skips if so. No ambiguity in practice.

---

## PP-V2-R7-09: @Background referencing function with no step decorators ⬇️ DROPPED

**Severity:** Low
**Location:** Background (line 93-103)

`@Background(func)` where `func` has no step decorators. Empty hash list matches empty cache entry (0 == 0).

**Dropped:** This is semantically meaningless but not harmful. No spec change needed.

---

## PP-V2-R7-10: Step text with literal <...> that looks like a placeholder ⬇️ DROPPED

**Severity:** Low
**Location:** Placeholder Syntax (line 148-183)

Step text like `"the page has <br> tag"` extracts `br` as a placeholder.

**Dropped:** This is inherent to the `<name>` syntax. `<br>` is a valid Python identifier. There's no way to distinguish "intentional placeholder" from "text that matches the pattern" without escaping conventions (which would complicate the simple syntax). Known limitation, not fixable.

---

## PP-V2-R7-11: Body enforcement fails when literal is constructed dynamically ⬇️ DROPPED

**Severity:** Low
**Location:** Body Enforcement (line 329-365)

AST-based enforcement can't find `"hello"` if the user writes `"hel" + "lo"`.

**Dropped:** Inherent limitation of AST analysis. Not fixable without symbolic execution. Acceptable trade-off — users should use literal values in tests that match Gherkin step text.

---

## PP-V2-R7-16: Title 'spaces' — U+0020 only or any Unicode whitespace? ⬇️ DROPPED

**Severity:** Low
**Location:** Title format rule (line 15)

Does "spaces" mean only U+0020 or any Unicode Zs character?

**Dropped:** In practice, Gherkin uses U+0020 (ASCII space). Non-breaking spaces and other Zs characters in titles would be confusing and rare. The parser accepts U+0020 only. No spec change needed — "spaces" unambiguously means the space character.

---

## PP-V2-R7-24: Clean command — does it remove empty test files? ⬇️ DROPPED

**Severity:** Low
**Location:** Clean Command (line 474-476)

After removing all orphan functions, the file is empty. Does clean delete it?

**Dropped:** Clean removes orphan functions, not files. An empty file with imports is harmless. If the user wants to delete the file, they can do so manually. No spec change needed.

---

## Summary

| Status | Count | IDs |
|--------|-------|-----|
| ✅ Resolved | 10 | R7-03, R7-05, R7-07, R7-13, R7-14, R7-15, R7-17, R7-20, R7-22, R7-27 |
| ⬇️ Dropped | 13 | R7-01, R7-01a, R7-02, R7-02a, R7-04, R7-06, R7-08, R7-09, R7-10, R7-11, R7-16, R7-24, R7-26 |
| ❌ Pending | 0 | |
| **Total** | **23** | |

### Spec Changes

| Change | Source |
|--------|--------|
| `outline_random_examples` controls `hypothesis.settings.max_examples` for Scenario Outline | R7-13 |
| Clarify Hypothesis stacking order: `@example` outermost, `@given` innermost | R7-03 |
| Background function must start with `@Given`/`@When`/`@Then` (not `@And`/`@But`) | R7-05 |
| Comments: `#` at line start ignored, literal inside table cells | R7-07 |
| `@Example` values must match inferred type (lists stay lists) | R7-14 |
| Parser transparently handles UTF-8 BOM | R7-15 |
| `@Example` on no-placeholder function → collection-time error | R7-17 |
| Boolean detection is case-insensitive | R7-20 |
| Multiple `@Background` must be in feature → rule order | R7-22 |
| Placeholder names must not shadow Python builtins | R7-27 |
