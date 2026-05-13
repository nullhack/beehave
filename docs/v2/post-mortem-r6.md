# beehave v2 Spec Post-Mortem — Round 6 (Adversarial Pipeline)

> Adversarial emulation targeting the R5 spec changes: Background composition,
> decorator resolution with @Background, cache structure coherence, and @Example
> set matching edge cases. Each issue was validated by implementing the spec
> literally and finding where it breaks.
> All artifacts in `/tmp/beehave-v2-r6/`.

---

## PP-V2-R6-05: @Example set matching breaks on composite types ✅ RESOLVED

**Severity:** High
**Location:** Collection-Time Check + @Example matching

Spec says `@Example` rows are compared as **sets** by exact value equality. But Python `set` and `frozenset` require hashable values. Examples columns can contain lists (`[1, 2, 3]`) and dicts (`{"a": 1}`) per the composite type inference rules. These types are **unhashable** — `frozenset(e.items())` raises `TypeError` for any row containing a list or dict value.

**Resolution:** Use deep equality bijection instead of set hashing. For each cached example row, find a matching `@Example` decorator using `==` (recursive equality for dicts/lists). Every cached row must have exactly one match, and every `@Example` must match exactly one cached row. O(n²) but Examples tables are tiny (<10 rows). Preserves set semantics (unordered, no duplicates counted twice) without requiring hashability.

---

## PP-V2-R6-06: Cache structure missing rule-level scenarios ✅ RESOLVED

**Severity:** High
**Location:** Cache structure + Collection-Time Check

The cache structure example shows `scenarios` at the feature level and `rules` with only a `background` key. Scenarios inside a Gherkin `Rule:` block have no cache entry showing their rule membership. Collection-time background resolution needs to know WHICH rule a scenario belongs to (to apply feature+rule background composition), but this information is absent from the cache.

**Resolution:** Add `scenarios` dict inside each rule entry. Every rule entry has a `scenarios` key (always present, possibly empty `{}`). A scenario inside a Rule is cached under that rule's `scenarios` dict. Feature-level `scenarios` contains only scenarios directly under the Feature (not inside any Rule). Collection-time lookup: scan feature-level scenarios first, then each rule's scenarios. Rule membership is known from cache position.

---

## PP-V2-R6-09: Strategy resolution — does it look inside @Background? ✅ RESOLVED

**Severity:** High
**Location:** Decorator Resolution + Strategy Resolution Trigger

Spec said strategy resolution fires "when ANY step across all decorators contains `<placeholders>`." But `@Background(func)` references a separate function whose step decorators contain `<placeholders>`. Does "all decorators" include the background function's step decorators?

**Resolution:** Background steps must NOT contain `<placeholders>` (see R6-17). This eliminates the question entirely — background functions have no placeholders to collect. The decorator resolution phase only collects placeholders from the test function's own step decorators.

---

## PP-V2-R6-16: Decorator Resolution algorithm missing @Background collection ✅ RESOLVED

**Severity:** High
**Location:** Decorator Resolution

The Decorator Resolution section (step 1) says "Collect step text and placeholder metadata from `@Given`/`@When`/`@Then`/`@And`/`@But`." It does not mention collecting from `@Background`'s referenced function. Same root cause as R6-09.

**Resolution:** Background steps cannot contain `<placeholders>` (see R6-17). No placeholder collection from @Background is needed. Decorator resolution step 1 remains unchanged — it only collects from the test function's own decorators.

---

## PP-V2-R6-17: Is @Background function wrapped with @given()? ✅ RESOLVED

**Severity:** High
**Location:** Decorator Resolution + Background

Background functions have step decorators with `<placeholders>`. Does beehave wrap the background function itself with `@given()`?

**Resolution:** Background steps must NOT contain `<placeholders>`. This is a parse error — the parser rejects `<...>` syntax in Background step text. Background is for fixed shared setup only, aligning with standard Gherkin (Cucumber explicitly rejected placeholders in Background). This eliminates the @given() wrapping question entirely. Background functions are metadata-only: their step decorators exist solely for vocabulary enforcement against cached Gherkin `Background:` sections.

---

## PP-V2-R6-07: @And inheritance check — per-function or combined? ✅ RESOLVED

**Severity:** Medium
**Location:** Background + @And/@But inheritance

Spec says `@And`/`@But` before any `@Given`/`@When`/`@Then` → collection-time error. But with background composition, a scenario may have `@And` as its first step decorator (inheriting from the background's `@Given` in the combined list). Does the error check run per-function or per-combined-list?

**Resolution:** The `@And`/`@But` inheritance check runs on the **combined list** (background + scenario). A scenario starting with `@And` is valid if a background step precedes it in the combined list. The error only fires if `@And`/`@But` appears and there is NO preceding `@Given`/`@When`/`@Then` anywhere in the combined list.

---

## PP-V2-R6-14: Duplicate Examples rows — set matching allows missing @Example ⬇️ DROPPED

**Severity:** Medium
**Location:** Collection-Time Check

A `.feature` file has Examples rows `[1, 1, 2]` (with duplicate). Python has `@Example(1) @Example(2)` (2 decorators, no duplicate). Set comparison passes because unique sets are `{1, 2}` in both cases. But there were 3 Examples rows and only 2 `@Example` decorators. One Examples row has no corresponding decorator. Is this correct behavior?

---

## PP-V2-R6-18: Examples values — strings or typed in cache? ✅ RESOLVED

**Severity:** Medium
**Location:** Cache structure + @Example matching

Generated `@Example` shows typed values (`@Example(amount=100)`), but the cache's `examples` field format was undefined. If the cache stores raw strings (`"100"`) and `@Example` uses typed values (`100`), comparison fails because `100 != "100"`.

**Resolution:** Cache stores **typed values** (coerced at parse time using the same type inference rules). `"100"` → `100` (int), `"0.1"` → `0.1` (float), `"Alice"` → `"Alice"` (str), `"true"` → `True` (bool). This matches what `generate` produces in Python `@Example` decorators.

---

## PP-V2-R6-19: Quoting inconsistency — flexible detection vs exact vocabulary ✅ RESOLVED

**Severity:** Medium
**Location:** Vocabulary enforcement + String detection

String detection auto-detects both `'` and `"` as quoting (spec: "auto-detects both ' and \" as quote chars"). But vocabulary enforcement is "case-sensitive and exact." If `.feature` uses `'<name>'` and Python uses `"<name>"`, both are string-typed, but vocabulary enforcement sees different characters and reports a mismatch.

**Resolution:** Vocabulary enforcement normalizes quote characters for string-typed placeholders before comparison. Both `'<name>'` and `"<name>"` are treated as equivalent template forms. The normalization applies only to the quote characters surrounding a `<placeholder>` — all other text is compared exactly.

---

## PP-V2-R6-20: fix command — does it update @Background step decorators? ✅ RESOLVED

**Severity:** Medium
**Location:** CLI + Fix command

`fix` aligns decorator text with `.feature` step text. But background steps belong to the `@Background` function, not the test function. If a `.feature` Background step changes, does `fix` also update the background function's step decorators?

**Resolution:** Yes, `fix` updates both test function step decorators AND `@Background` function step decorators when the corresponding `.feature` content changes. Fix operates on the feature file's scope — all step decorators mapping to the changed `.feature` content are updated.

---

## PP-V2-R6-21: Scenario Outline with Examples column not in any step ✅ RESOLVED

**Severity:** Medium
**Location:** Scenario Outline + Examples + Parameter Binding

A Scenario Outline can have Examples columns that don't correspond to any `<placeholder>` in step text. The generated `@Example` would include the column value, but without a matching `@given()` kwarg, Hypothesis raises `InconsistentArgsError`.

**Resolution:** Parse-time validation: every Examples column header must correspond to a `<placeholder>` in the scenario's step list. Unreferenced columns → parse error: "Examples column 'X' has no matching `<X>` in any step."

---

## PP-V2-R6-22: Cache `examples` field format undefined ✅ RESOLVED

**Severity:** Medium
**Location:** Cache structure

The cache structure shows `"examples": []` for plain scenarios but never shows a populated `examples` field for Scenario Outlines. Format (typed vs string, dict vs list) is undefined.

**Resolution:** The `examples` field stores a list of dicts with **typed values** (coerced at parse time). See R6-18.

---

## PP-V2-R6-11: Rule with Background but no scenarios ⬇️ DROPPED

**Severity:** Low
**Location:** Traceability parser

A Gherkin Rule with a Background but no scenarios. The background is never applied. Valid Gherkin but semantically meaningless.

---

## Summary

| Status | Count | IDs |
|--------|-------|-----|
| ✅ Resolved | 11 | R6-05, R6-06, R6-07, R6-09, R6-16, R6-17, R6-18, R6-19, R6-20, R6-21, R6-22 |
| ⬇️ Dropped | 2 | R6-11, R6-14 |
| ❌ Pending | 0 | |
| **Total** | **13** | |

### Spec Changes

| Change | Source |
|--------|--------|
| @Example matching: deep equality bijection (supports composite types) | R6-05 |
| Cache structure: `scenarios` dict inside each rule entry (always present, possibly empty) | R6-06 |
| Background: no `<placeholders>` allowed — parse error if found | R6-09, R6-16, R6-17 |
| @And/@But inheritance check runs on combined list, not per-function | R6-07 |
| Cache examples: typed values (coerced at parse time) | R6-18, R6-22 |
| Vocabulary enforcement: normalize quote chars for string-typed placeholders | R6-19 |
| Fix command: updates @Background function step decorators too | R6-20 |
| Parse-time validation: every Examples column must match a `<placeholder>` in steps | R6-21 |

### R5 Post-Mortem Revision

R5-03 resolution was revised: instead of requiring Background placeholders as Examples columns, Background steps are now prohibited from containing `<placeholders>` entirely. This aligns with standard Gherkin and eliminates the fill-value / cross-boundary parameter binding problem.
