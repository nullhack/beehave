# beehave v2 Spec Post-Mortem — Round 3 (Adversarial Pipeline)

> Full pipeline adversarial emulation: parse → generate → vocabulary → body enforcement → fix → clean.
> Focused on realistic feature files and cross-feature interactions.
> All artifacts in `/tmp/beehave-v2-emulation/`.

---

## PP-V2-R3-01: Examples table overrides quoting but quoted placeholder expects text — **RESOLVED**

**Severity:** Medium
**Location:** Strategy inference

A placeholder like `'<name>'` (quoted, expects text) has an Examples column with integers. Examples wins per priority, but the user explicitly signaled "string."

**Resolution:** Examples table wins, but beehave emits a warning suggesting the user resolve the inconsistency.

---

## PP-V2-R3-02: Body enforcement matches placeholder names in comments — **RESOLVED**

**Severity:** Low
**Location:** Validation

`# calculate remaining` passes body enforcement because `remaining` appears in a comment.

**Resolution:** Body enforcement uses AST analysis — only actual code references count, not comments or string literals.

---

## PP-V2-R3-04: Step count mismatch between decorator and Gherkin not handled — **RESOLVED**

**Severity:** High
**Location:** Validation

Test has 2 step decorators but Gherkin scenario has 3 steps. Simple string comparison didn't catch the missing step.

**Resolution:** Vocabulary enforcement redesigned as hash-based 1:1 ordered matching with a persistent cache file (`.beehave/cache.json`). See Vocabulary Enforcement section in spec.

---

## PP-V2-R3-05: Vocabulary enforcement requires steps in same order — **RESOLVED**

**Severity:** Medium
**Location:** Validation

Steps in different order produce the same hashes but different behavior.

**Resolution:** Order matters. Hash-based matching is position-sensitive — step N in the test must match step N in the cache.

---

## PP-V2-R3-06: Background vocabulary enforcement source unclear — **RESOLVED**

**Severity:** Medium
**Location:** Validation

Background steps are Python-only, not in the `.feature` file. What does vocabulary enforcement check them against?

**Resolution:** Cache stores combined step hashes (background + scenario from the `.feature` file). Collection-time check prepends `@Background` step decorators to the test's decorators, then matches the combined list against the cache.

---

## PP-V2-R3-07: Scenario Outline — random generation beyond @Example — **RESOLVED**

**Severity:** Medium
**Location:** Decorator resolution

`@Example` + `@given()` means Hypothesis runs Example values AND generates random cases. Scenario Outline typically means "test only these specific examples."

**Resolution:** Examples + random generation (option B + C). Default: 1 random Hypothesis case beyond Examples. Configurable via `outline_random_examples` setting (0 = Example-only).

---

## PP-V2-R3-08: Multiple Examples tables per Scenario Outline — **RESOLVED**

**Severity:** Medium
**Location:** Traceability parser

Standard Gherkin allows multiple named `Examples:` tables. beehave didn't address this.

**Resolution:** All Examples tables are merged into a single `@Example` set. Table names are ignored.

---

## Summary

| Status | Count |
|--------|-------|
| Resolved | 7 |
| Dropped | 0 |
| **Total** | **7** |

### Spec Changes

| Change | Source |
|--------|--------|
| Examples/quoting conflict → warning | R3-01 |
| Body enforcement → AST-based (skips comments) | R3-02 |
| Vocabulary enforcement → hash-based 1:1 ordered match with `.beehave/cache.json` | R3-04, R3-05, R3-06 |
| `outline_random_examples` config setting (default: 1) | R3-07 |
| Multiple Examples tables → merge all rows | R3-08 |
| `fix` and `clean` commands described in Vocabulary Enforcement section | R3-04 |
