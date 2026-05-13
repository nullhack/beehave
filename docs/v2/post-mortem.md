# beehave v2 Spec Post-Mortem

> Spec emulation executed against `docs/spec/beehave_v2_spec.md`. Full pipeline emulation
> (parse → validate → generate → collect → fix → clean) with edge case testing.
> All artifacts in `/tmp/beehave-v2-emulation/`.

---

## PP-V2-01: Spec example uses raw `@given()` instead of `@Given` — **RESOLVED**

**Severity:** Medium
**Location:** `beehave_v2_spec.md:214`

The Scenario Outline example showed raw `@given()` which users should never write.

**Resolution:** Spec now shows user-facing API (`@Given`/`@When`/`@Then`/`@Example`) with a separate "Under the hood" block showing the Hypothesis resolution.

---

## PP-V2-02: CLI generate description has wrong strategy priority — **RESOLVED**

**Severity:** High
**Location:** `beehave_v2_spec.md:288`

CLI description said "user override > quoting > Examples > default" but priority table says "user > Examples > quoting > default".

**Resolution:** Fixed to `user override > Examples table > quoting > default`.

---

## PP-V2-03: Interaction between `@Given` and `@Example` is undefined — **RESOLVED**

**Severity:** High
**Location:** `beehave_v2_spec.md:211–218`

`@Example` ↔ `@Given` interaction and Hypothesis mapping was undefined.

**Resolution:** Added "Decorator Resolution" section. beehave decorators are metadata collectors. At import time, beehave collects all decorators, then wraps with `@hypothesis.given(**strategies)` and `@hypothesis.example(**values)` in correct stacking order. User-facing decorator order follows Gherkin convention.

---

## PP-V2-04: `@And`/`@But` inheritance across decorators is ambiguous — **RESOLVED**

**Severity:** Medium
**Location:** `beehave_v2_spec.md:40`

**Resolution:** `@And`/`@But` inherit from the immediately preceding `@Given`/`@When`/`@Then` on the same function. If no preceding step type exists → collection-time error. Also added `@Background(func)` decorator that injects background steps before scenario steps. `@And`/`@But` inheritance works across the combined (background + scenario) list.

---

## PP-V2-05: Body enforcement scope for Scenario Outline unclear — **RESOLVED**

**Severity:** Low
**Location:** `beehave_v2_spec.md:222–259`

**Resolution:** Added clarification: "For Scenario Outline, enforcement checks the shared function body once — not per-Example execution."

---

## PP-V2-06: `@Example` with unknown placeholder name has undefined behavior — **RESOLVED**

**Severity:** Medium
**Location:** `beehave_v2_spec.md:329`

**Resolution:** `@Example` keys must match placeholder names exactly. Unknown or missing keys → collection-time error.

---

## PP-V2-07: Literal enforcement may false-positive on substrings — **RESOLVED**

**Severity:** Medium
**Location:** `beehave_v2_spec.md:243–258`

**Resolution:** Whole-word matching using `\b` word boundaries for numeric literals. Quoted strings match exactly. Symbols attached to numbers (e.g., `1%`) must be quoted (`'1%'`) to enforce as string literal.

---

## PP-V2-08: Quote detection ambiguous for placeholders inside path-like strings — **DROPPED**

**Severity:** High → Not a real issue
**Location:** `beehave_v2_spec.md:84–94`

**Resolution:** Dropped. The rule is already clear — only immediately adjacent quote characters trigger string detection. No ambiguity.

---

## PP-V2-09: `auto_inference=false` interaction with Examples table unclear — **RESOLVED**

**Severity:** Medium
**Location:** `beehave_v2_spec.md:395`

**Resolution:** `auto_inference=false` disables strategy inference only. Examples table values are still read to generate `@Example` concrete values — they just don't infer strategies. User must define strategies manually.

---

## PP-V2-10: Vocabulary enforcement with placeholders undefined — **RESOLVED**

**Severity:** High → Clarification only
**Location:** `beehave_v2_spec.md:262–271`

**Resolution:** Added clarification: matching is on the template form — placeholder syntax `<name>` is compared literally, not resolved to values. Both sides always have the template form.

---

## PP-V2-11: Module-level variable override scope is per-file, not per-test — **RESOLVED**

**Severity:** High
**Location:** `beehave_v2_spec.md:150–159`

**Resolution:** Documented that module-level overrides apply to all tests in the file. If different strategies are needed for the same placeholder name, split the tests into separate files. No per-test override mechanism in v2.

---

## PP-V2-12: `Scenario Outline` without `Examples` table is undefined — **RESOLVED**

**Severity:** Medium
**Location:** Not addressed in spec

**Resolution:** `Scenario Outline` requires at least one `Examples:` table with at least one data row. If missing → parse error.

---

## Summary

| Status | Count |
|--------|-------|
| Resolved | 10 |
| Dropped | 1 |
| **Total** | **11** |

### New Spec Additions

| Addition | Source |
|----------|--------|
| Decorator Resolution section | PP-V2-03 |
| `@Background(func)` decorator | PP-V2-04 |
| Background rules (7 rules) | PP-V2-04 |
| Whole-word literal matching | PP-V2-07 |
| Vocabulary enforcement template form clarification | PP-V2-10 |
| Per-file override scope documentation | PP-V2-11 |
| Scenario Outline requires Examples | PP-V2-12 |
