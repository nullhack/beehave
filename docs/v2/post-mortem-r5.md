# beehave v2 Spec Post-Mortem — Round 5 (Adversarial Pipeline)

> Adversarial emulation focusing on spec contradictions, wrong specifications,
> and implementation blockers. Each issue was validated by attempting to implement
> the spec literally and finding where it breaks.
> All artifacts in `/tmp/beehave-v2-r5/`.

---

## PP-V2-R5-01: Background vocabulary enforcement is contradictory ✅ RESOLVED

**Severity:** High
**Location:** Vocabulary enforcement + Background + Cache

Cache is built from `.feature` files only. Background steps are Python-only (`@Background(func)`). At collection time, combined list (background + scenario) has more steps than the cache → vocabulary enforcement always fails for any test using `@Background`.

**Resolution:** Parse Gherkin `Background:` sections from `.feature` files into the cache at feature level. `@Background(func)` in Python is vocabulary-verified against cached background steps. Both sides must match — feature file has `Background:` section iff test has `@Background` decorator. Gherkin Rules may also have `Background:` sections; backgrounds compose (feature background + rule background), matched by multiple `@Background` decorators on the test function.

---

## PP-V2-R5-02: Placeholders in @When/@Then without @Given have no strategy binding ✅ RESOLVED

**Severity:** High
**Location:** Step Decorators + Hypothesis Binding

Spec said only `@Given` applies `@given()`. A scenario with only `@When`/`@Then` steps containing placeholders has params but no `@given()` wrapping → TypeError at collection.

**Resolution:** All step decorators (`@Given`, `@When`, `@Then`) are pure metadata collectors. Strategy resolution and `@given()` wrapping are applied by the decorator resolution phase when ANY step across all decorators contains `<placeholders>`. No single decorator type is responsible for triggering Hypothesis wiring.

---

## PP-V2-R5-03: Strategy "default value" for @Example fill-in doesn't exist ✅ RESOLVED

**Severity:** High
**Location:** Parameter Binding + Background

Spec said "strategy's default value (e.g., `0` for `st.integers()`)" for filling `@Example` rows when a placeholder has no Examples column. But `st.integers()` has no default value. For user overrides like `st.integers(min_value=100)`, using `0` may be outside the strategy's range. The root cause: Hypothesis requires `@example()` to declare ALL `@given()` params, but Gherkin Examples tables conventionally only contain scenario-level columns, not Background-level columns.

**Resolution (revised in R6):** Background steps must NOT contain `<placeholders>`. This aligns with standard Gherkin (Cucumber explicitly rejected placeholders in Background). Background is for fixed shared setup only. Parameterized setup should use plain Scenario with `@Given` steps containing `<placeholders>`. This eliminates the fill-value problem entirely — no Background placeholders means no cross-boundary parameter binding complexity.

---

## PP-V2-R5-04: Multiple Examples tables with different column sets undefined ✅ RESOLVED

**Severity:** Medium
**Location:** Scenario Outline + Examples

Spec said "all rows are merged" but didn't define behavior when tables have different column sets (union? error?).

**Resolution:** All `Examples:` tables within a single Scenario Outline must have identical column headers (same names, same order). Different columns → parse error indicating which tables are inconsistent. This ensures every `@Example` row has the same parameter coverage.

---

## PP-V2-R5-06: Cache lookup: title → function name → title round-trip is lossy ✅ RESOLVED

**Severity:** Medium
**Location:** Cache structure + Collection-Time Check

Cache keyed by raw title, but lookup reverses from function name → title is lossy. Titles with consecutive spaces collapse to single underscores and can't be recovered.

**Resolution:** Add `function_name` to each cache entry (computed at cache build time from the title). Collection-time lookup scans cache entries for matching `function_name` instead of reverse-mapping from function name to title.

---

## PP-V2-R5-07: @Example ordering: is it positional or set-based? ✅ RESOLVED

**Severity:** Medium
**Location:** Collection-Time Check

Spec said "@Example rows matched 1:1 by exact values" which implied ordered matching. But `@Example` rows are semantically a set — Hypothesis runs each independently, order doesn't affect semantics.

**Resolution:** Set-based matching. The set of `@Example` decorator values must exactly equal the set of cached Examples row values. Order doesn't matter. Duplicate rows (identical across all columns) count once in the set comparison.

---

## PP-V2-R5-08: Mixed int/float in Examples falls back to st.integers() ⬇️ DROPPED

**Severity:** Low → Not a real issue
**Location:** Strategy inference

Emulation claimed mixed int/float columns (e.g., `[1, 1.0]`) would fall back to `st.integers()` incorrectly.

**Resolution:** False positive. Column type inference already takes the most general type per column. If any row has a float, the entire column infers `st.floats()`. The "mixed types" fallback only applies to truly incompatible types (e.g., int + string). Not a spec bug.

---

## PP-V2-R5-09: Gherkin Background: section in .feature files is unhandled ✅ RESOLVED

**Severity:** Medium
**Location:** Traceability parser

Standard Gherkin has `Background:` sections. beehave v2 had no parser behavior defined for them. Merged with R5-01 resolution.

**Resolution:** Parse `Background:` sections from `.feature` files. Stored in cache at feature level. See R5-01.

---

## Summary

| Status | Count | IDs |
|--------|-------|-----|
| ✅ Resolved | 7 | R5-01, R5-02, R5-03, R5-04, R5-06, R5-07, R5-09 |
| ⬇️ Dropped | 1 | R5-08 |
| **Total** | **8** | |

### Spec Changes

| Change | Source |
|--------|--------|
| Background section rewritten: Gherkin `Background:` parsed into cache, feature+rule composition, bilateral verification | R5-01, R5-09 |
| Background rule 11: Background placeholders must appear as Examples columns in Scenario Outline | R5-03 |
| Step decorators: all are metadata collectors, strategy binding in resolution phase | R5-02 |
| Hypothesis binding: triggered by any step with placeholders, not just @Given | R5-02 |
| Cache structure: added `background` field, `function_name` field per scenario | R5-01, R5-06 |
| Collection-Time Check: background resolution, function_name lookup, set-based @Example | R5-01, R5-06, R5-07 |
| Examples tables: identical column headers required, must cover all combined placeholders | R5-04, R5-03 |
| Parameter Binding: removed fill-value language, requires Background columns in Examples | R5-03 |
| Gherkin Extensions table: added Background `<placeholder>` extension entry | R5-03 |
| Architecture section: updated decorator descriptions | R5-02 |
