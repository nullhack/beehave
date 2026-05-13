# beehave v2 Spec Post-Mortem — Round 4 (Adversarial Pipeline)

> Full adversarial emulation targeting cache lifecycle, fix/clean commands,
> decorator resolution, background + Scenario Outline, composite edge cases,
> Unicode normalization, and error recovery paths.
> All artifacts in `/tmp/beehave-v2-emulation/`.

---

## PP-V2-R4-01: Cache invalidation: what triggers a rebuild? ✅ RESOLVED

**Severity:** Medium
**Location:** Vocabulary enforcement

Spec said "updated when .feature files change (compared by edit time)." But: (1) What if the user deletes `.beehave/cache.json`? (2) What if the user edits the test file but not the feature file? (3) What if the user renames a `.feature` file?

**Resolution:** Switched from edit time to SHA-256 content hashing. Full cache lifecycle defined:
- Missing cache → silent rebuild
- Feature file changed (hash mismatch) → rebuild that entry
- Feature file deleted → remove stale entry
- Feature file renamed → deletion + addition
- New feature file → detected and parsed
- Test file edited → cache unaffected (cache only tracks feature files)
- Every operation validates cache first (incremental hash checks)
- `.beehave/` added to `.gitignore` — cache is a derived artifact

---

## PP-V2-R4-02: Fix command: does it update function parameters? ✅ RESOLVED

**Severity:** Medium
**Location:** CLI

If a `.feature` step gains a new `<placeholder>`, fix updates the decorator text. But does fix also add the new parameter to the function signature? If not, the function will fail at runtime.

**Resolution:** Fix only updates decorator text — it does NOT modify function signatures, parameters, bodies, or imports. Two detection layers catch the gap: (1) Python `TypeError` at import time if `@given()` provides a param the function doesn't accept, (2) body enforcement if a placeholder isn't referenced in the body. Orphan parameter detection added to `clean` command — flags params in signature not present in `@given()` kwargs.

---

## PP-V2-R4-03: Fix command: does it update @Example decorators? ⬇️ DROPPED

**Severity:** Low
**Location:** CLI

If the `.feature` file's Examples table changes (rows added/removed/modified), does fix update the `@Example` decorators?

**Resolution:** Low priority, deferred. Fix scope is decorator text only. @Example updates can be addressed in a future iteration.

---

## PP-V2-R4-04: Clean command: deletes orphan instead of suggesting rename ⬇️ DROPPED

**Severity:** Low
**Location:** CLI

When a scenario is renamed, the old test function becomes an orphan. Clean deletes it, losing the test body.

**Resolution:** Noted for future UX improvement. Not blocking.

---

## PP-V2-R4-05: Decorator collection order: source order vs feature file order ✅ RESOLVED

**Severity:** High
**Location:** Decorator resolution

Spec said decorators are collected "in the order they appear in the feature file." But decorators are on Python functions. The user can reorder them.

**Resolution:** Decorators are collected in Gherkin order as written by `generate`. The cache's hash sequence defines the canonical ordering. Vocabulary enforcement matches positionally. Do not reorder step decorators. This is a spec clarification, not a code change — no one naturally reorders decorators, and ordered matching catches accidental swaps.

---

## PP-V2-R4-06: Background placeholders + Scenario Outline Examples interaction ✅ RESOLVED

**Severity:** High
**Location:** Parameter binding

Background has `<user_id>`, Scenario Outline has `<amount>` with Examples table. The Examples table only has `amount` column. Should `@Example` include `user_id`?

**Resolution:** All placeholders become `@given` params (one consistent rule). `@Example` rows include values for ALL params — those from both Background and scenario steps. For placeholders without an Examples table column, the strategy's default value is used (e.g., `0` for `st.integers()`, `""` for `st.text()`). This satisfies Hypothesis's constraint that `@example()` must specify every `@given()` param. No special-casing on "did this come from Background?"

---

## PP-V2-R4-07: Nested composite types not addressed ⬇️ DROPPED

**Severity:** Low
**Location:** Strategy inference

Examples cell `{"a": [1, 2]}` is a dict with list values. Spec only shows flat composites.

**Resolution:** Nested composites are user override territory. Users define the strategy manually for complex structures.

---

## PP-V2-R4-08: Empty composite values have no inner type to infer ⬇️ DROPPED

**Severity:** Medium
**Location:** Strategy inference

Examples cell `[]` is an empty list. No inner type to infer.

**Resolution:** Stakeholder assessed as unlikely scenario. Users writing `[]` in an Examples cell would define the strategy manually.

---

## PP-V2-R4-09: Unicode normalization affects vocabulary hash comparison ⬇️ DROPPED

**Severity:** Low
**Location:** Vocabulary enforcement

`café` (NFC) and `café` (NFD) produce different hashes. If `.feature` and decorator use different normalizations, vocabulary enforcement reports a mismatch.

**Resolution:** Theoretical concern — same editor typically produces same normalization. Not worth the complexity.

---

## PP-V2-R4-10: auto_inference=false: partial strategy definition undefined ✅ RESOLVED

**Severity:** Medium
**Location:** Configuration

User defines `initial` but forgets `amount`. Spec said "Parser errors on undefined strategy vars" but didn't specify when.

**Resolution:** Error fires at collection time (when beehave has full context: step text placeholders, module namespace, auto_inference flag). Aggregates all missing strategies before raising — one error listing all missing definitions. `generate` doesn't error because stubs don't exist yet. Examples values are still read for `@Example` even with `auto_inference=false` — only strategy inference is disabled.

---

## PP-V2-R4-11: @Example value types vs inferred strategy types ⬇️ DROPPED

**Severity:** Low
**Location:** Decorator resolution

`@Example(balance_a=100.0)` passes a float for an integer-inferred column.

**Resolution:** No type enforcement on @Example values — Hypothesis handles type mismatches at runtime. This is the correct boundary.

---

## PP-V2-R4-12: Multiple @Given decorators on same function ✅ RESOLVED

**Severity:** Medium
**Location:** Decorator resolution

A function with two `@Given` decorators is valid Python. Is this allowed?

**Resolution:** Yes, allowed. Maps to multiple Given steps in the Gherkin. Vocabulary enforcement matches by position as usual. This is consistent with how `@And` works (continuation of Given) — multiple `@Given` just means multiple explicit Given steps.

---

## PP-V2-R4-13: Feature file with no scenarios ⬇️ DROPPED

**Severity:** Low
**Location:** Traceability parser

A `.feature` file with `Feature: name` but no scenarios.

**Resolution:** Valid — produces no cache entries, no test stubs. No-op.

---

## PP-V2-R4-14: Scenario with no steps undefined ✅ RESOLVED

**Severity:** Medium
**Location:** Traceability parser

A Scenario with a title but no Given/When/Then steps. The test function would have no beehave step decorators.

**Resolution:** Parse error. A scenario with no steps has no behavior to test — it's meaningless. The parser rejects scenarios with zero steps.

---

## PP-V2-R4-15: How does beehave know a function is a background, not a test? ✅ RESOLVED

**Severity:** Medium
**Location:** Background

Background function is "not discovered by test runners." But if it starts with `test_`, pytest discovers it.

**Resolution:** `generate` controls the name — background functions won't be named `test_*`. If a user manually writes one with `test_*`, pytest discovers it — that's user error, not a beehave concern. No special internal marking needed.

---

## Summary

| Status | Count | IDs |
|--------|-------|-----|
| ✅ Resolved | 8 | R4-01, R4-02, R4-05, R4-06, R4-10, R4-12, R4-14, R4-15 |
| ⬇️ Dropped | 7 | R4-03, R4-04, R4-07, R4-08, R4-09, R4-11, R4-13 |
| ❌ Pending | 0 | |
| **Total** | **15** | |
