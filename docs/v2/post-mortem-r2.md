# beehave v2 Spec Post-Mortem — Round 2 (Adversarial)

> Adversarial emulation of the updated `docs/spec/beehave_v2_spec.md` after all Round 1
> pain points were resolved. Tests every spec rule against edge cases designed to break them.
> All artifacts in `/tmp/beehave-v2-emulation/`.

---

## PP-V2-R2-01: Empty title passes validation

**Severity:** High
**Location:** `beehave.traceability` — title validation

`Scenario: ` (empty after trim) passes the Unicode letter/digit/space check because there are no invalid characters — just nothing. Function name would be `test_` which is valid but meaningless.

**Remediation:** Parser must reject empty titles (after trimming whitespace). Error: "Scenario title cannot be empty."

---

## PP-V2-R2-02: All-spaces title passes validation

**Severity:** Medium
**Location:** `beehave.traceability` — title validation

`Scenario:    ` (all spaces) has no invalid characters. Function name would be `test___` (underscores from spaces). The title is effectively empty.

**Remediation:** After trimming, if the title is empty or whitespace-only → reject.

---

## PP-V2-R2-03: Multiple spaces produce multiple underscores in function name

**Severity:** Low
**Location:** `beehave.traceability` — title-to-function-name conversion

`"a   b"` → `test_a___b` (triple underscore). Should collapse consecutive underscores.

**Remediation:** After space→underscore conversion, collapse consecutive `_` to single `_`.

---

## PP-V2-R2-04: Titles differing only in whitespace not caught as duplicates

**Severity:** High
**Location:** `beehave.validation` — global uniqueness check

`"user login"` and `"user  login"` (double space) both produce `test_user_login`. The uniqueness check compares function names, which already normalizes multiple spaces to single underscores — so this is caught IF underscores are collapsed (see R2-03). But if underscores are NOT collapsed, `test_user__login` vs `test_user_login` would not collide.

**Remediation:** Both R2-03 (collapse underscores) and uniqueness check on the normalized function name are needed.

---

## PP-V2-R2-05: Placeholder named with Python keyword

**Severity:** High
**Location:** `beehave.cli` — `generate` command

`<class>` produces parameter `class` → SyntaxError in generated stub. The spec has no rule against Python keywords as placeholder names. Similarly: `<return>`, `<import>`, `<def>`, `<for>`, `<while>`, etc.

**Remediation:** Define a rule: placeholder names must be valid Python identifiers AND not Python keywords. Parser rejects invalid placeholder names at parse time.

---

## PP-V2-R2-06: Placeholder name with spaces

**Severity:** Medium
**Location:** `beehave.cli` — `generate` command

`<my name>` produces parameter `my name` → SyntaxError. The spec has no constraint on placeholder name format.

**Remediation:** Placeholder names must be valid Python identifiers (letters, digits, underscores, no spaces).

---

## PP-V2-R2-07: Placeholder name with special characters

**Severity:** Medium
**Location:** `beehave.cli` — `generate` command

`<count!>` produces parameter `count!` → SyntaxError. Same root cause as R2-06.

**Remediation:** Same as R2-06 — placeholder names must be valid Python identifiers.

---

## PP-V2-R2-08: Empty Examples cell behavior undefined

**Severity:** Medium
**Location:** `beehave.traceability` — Examples table parsing

An empty cell `||` in an Examples table is inferred as `text` (empty string fallback). Is this correct? Should it be an error? Or is empty string a valid value?

**Remediation:** Define behavior: empty cell = empty string (`""`). It's a valid `st.text()` value.

---

## PP-V2-R2-09: Word boundary false positive on variable names (NOT a spec issue)

**Severity:** Low → Not a real issue
**Location:** `beehave.validation` — body enforcement

Testing showed `\b1\b` correctly does NOT match `x1` or `10`. The emulation script had a bug, not the spec. Whole-word matching works correctly.

**Resolution:** Dropped — not a real issue.

---

## PP-V2-R2-11: Vocabulary enforcement case sensitivity undefined

**Severity:** Medium
**Location:** `beehave.validation` — vocabulary enforcement

`"a user with balance <initial>"` vs `"A user with balance <initial>"` — exact matching says these are different. But Gherkin keywords (`Given`/`given`/`GIVEN`) are case-insensitive. Is step text case-sensitive?

**Remediation:** Decide: (a) case-sensitive step text matching (strict, matches spec "exact"), or (b) case-insensitive (more forgiving, consistent with Gherkin keyword handling).

---

## PP-V2-R2-12: `@Example` without step decorators is undefined

**Severity:** Medium
**Location:** `beehave.decorators`

What if a function has only `@Example` decorators but no `@Given`/`@When`/`@Then`? No vocabulary enforcement, no strategy inference. Is this valid?

**Remediation:** Define: a test function must have at least one step decorator (`@Given`/`@When`/`@Then`). `@Example` without any step decorator → collection-time error.

---

## PP-V2-R2-13: `auto_inference=false` quoting interaction needs verification

**Severity:** Low
**Location:** `beehave.configuration`

When `auto_inference=false`, does `'<name>'` in step text still extract the placeholder? Yes — the placeholder is extracted regardless. Only the strategy inference from quoting is disabled. The user must define the strategy manually.

**Resolution:** Clarification only, not a spec change. The spec already says this correctly.

---

## Summary

| Status | Count | IDs |
|--------|-------|-----|
| Resolved | 6 | R2-01, R2-02, R2-03, R2-04, R2-05, R2-06, R2-07, R2-08, R2-11 |
| Dropped | 3 | R2-09 (not a real issue), R2-12 (prevented by Gherkin parser + vocabulary enforcement), R2-13 (clarification only) |

### Resolutions

| ID | Resolution |
|----|-----------|
| R2-01/02 | Titles must be non-empty after trimming whitespace → parse error |
| R2-03/04 | Consecutive underscores collapsed; uniqueness checked on normalized name |
| R2-05/06/07 | Placeholder names must be valid Python identifiers, not keywords → parser rejects |
| R2-08 | Empty Examples cells = empty string `""`, inferred as `st.text()` |
| R2-11 | Vocabulary enforcement is case-sensitive, exact match |
| R2-12 | Dropped — Gherkin parser + vocabulary enforcement prevent this naturally |
| R2-13 | Dropped — spec already correct |
