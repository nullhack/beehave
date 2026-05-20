# Simulation Results: Case Insensitive Matching

> **Timestamp:** 2026-05-20T07:38:18Z
> **Contexts simulated:** Feature Parsing, Test Discovery, Consistency Checking
> **Iteration:** 2 of 5 (re-simulation after fix-spec)

---

## Walkthroughs Performed

### Prior Walkthroughs (Iteration 1 — Still Valid)

All 29 walkthroughs from iteration 1 (`.cache/sim/simulation_results_20260520T071043.md`) remain valid. The domain_spec `_extract_literals` regex change from `^-?\d+$` to `^-?\d+(\.\d+)?$` does not invalidate any prior walkthrough — it only expands coverage to include floats.

| # | Type | Input / Condition | Expected Output | Discovered Rule |
|---|------|------------------|----------------|-----------------|
| 1 | Happy path | Step "Given a dog named \<name\>" — valid Python identifier | Placeholder(name="name") extracted | Placeholder Extraction Valid Tokens |
| 2 | Edge case | Step 'Given a user named "\<username\>"' — placeholder inside quotes | Placeholder(name="username") extracted, Literal NOT created for "\<username\>" | Quoted Placeholder Not Double Captured |
| 3 | Edge case | Step "Given we use the \<class\> instance" — keyword token | No Placeholder extracted (keyword rejected) | Placeholder Extraction Valid Tokens |
| 4 | Edge case | Step "Given the value is \<int\>" — builtin token | No Placeholder extracted (builtin rejected) | Placeholder Extraction Valid Tokens |
| 5 | Edge case | Step "Given \<name\> meets \<name\>" — duplicate token | Single Placeholder(name="name") | Placeholder Extraction Valid Tokens |
| 6 | Edge case | Step "Given product \<ID\> is also known as \<id\>" — case variants | Two Placeholders: ID and id | (extraction detail) |
| 7 | Happy path | Step "Given 3 items" — numeric token | Literal(value=3, type=numeric) | Numeric Literal Extraction |
| 8 | Edge case | Step "Given the balance is -2010" — negative numeric token | Literal(value=-2010, type=numeric) | Negative Numbers Visible In Body |
| 9 | Happy path | Step 'Given a dog named "Rex"' — quoted string | Literal(value="Rex", type=string) | Literal Matching Case Insensitive |
| 10 | Edge case | Step 'Given a phone number "[PHONE]"' — bracket notation | Literal(value="[PHONE]") captured verbatim | Bracket Notation Preserved As Literal |
| 11 | Bug #19 before | Step '"\<name\>" in scenario outline' — current code | BOTH Placeholder AND Literal("\<name\>") | Quoted Placeholder Not Double Captured |
| 12 | Bug #19 after | Same input, fixed code | Placeholder only, no Literal | Quoted Placeholder Not Double Captured |
| 13 | Happy path | Body: x=42, y=77000, name="Rex" | body_constant_nodes: [42, 77000, "Rex"] | AST Body Constants Collected |
| 14 | Happy path | Body: balance=-2010, temp=-3.14 (UnaryOp) | body_constant_nodes: [2010, -2010, 3.14, -3.14] | Negative Numbers Visible In Body |
| 15 | Bug #18 before | Body: balance=-2010, current code (no UnaryOp folding) | body_constant_nodes: [2010, 5] — -2010 MISSING | Negative Numbers Visible In Body |
| 16 | Bug #18 after | Same input, fixed code (UnaryOp folding) | body_constant_nodes: [2010, -2010, 5] — -2010 PRESENT | Negative Numbers Visible In Body |
| 17 | Edge case | Body: docstring + x=42 | Docstring excluded, only [42] in constants | AST Body Constants Collected |
| 18 | Happy path | Body: dog=Dog(), balance=get_balance(), BALANCE=100 | body_name_nodes: ["dog", "balance", "BALANCE", "Dog"] | Placeholder Matching Case Insensitive |
| 19 | Happy path | \<Dog\> vs body Name "dog" — same case | Match — zero violations | Placeholder Matching Case Insensitive |
| 20 | Edge case | \<Dog\> vs body Name "DOG" — uppercase | Match via lowered comparison | Placeholder Matching Case Insensitive |
| 21 | Edge case | \<Dog\> vs body Names {"cat", "owner"} — no match | missing-placeholder violation | Placeholder Matching Case Insensitive |
| 22 | Happy path | "Rex" vs body Constant "Rex" — same case | Match — zero violations | Literal Matching Case Insensitive |
| 23 | Edge case | "Rex" vs body Constant "rex" — lowercase | Match via lowered comparison | Literal Matching Case Insensitive |
| 24 | Bug #22 before | Gherkin int(77000) vs Decimal("77000") → str("77000"), no normalization | String "77000" vs int 77000 → false positive missing-literal | Literal Matching Case Insensitive |
| 25 | Bug #22 after | Same input, string normalization active | str(77000) → "77000", {"77000"} → match — zero violations | Literal Matching Case Insensitive |
| 26 | Edge case | Gherkin literal 1 vs body Constant True | "1" ≠ "true" → missing-literal violation | True And One Never Collide |
| 27 | E2E happy path | Full pipeline: \<Dog\> + "Rex" + -2010 in Gherkin, dog + "rex" + -2010 in body | All 3 contexts produce correct output, zero violations | (E2E validation) |
| 28 | Error path | Stub test body (pass only) | Zero violations — stubs skip all checks | Stub Tests Skip All Checks |
| 29 | Error path | Scenario with no matching test | unmapped-scenario violation | (existing invariant) |

### New Walkthroughs (Iteration 2 — Missed Edge Cases)

| # | Type | Input / Condition | Expected Output | Discovered Rule |
|---|------|------------------|----------------|-----------------|
| 30 | Edge case | \<PhoneNumber\> vs body name "phone_number" | missing-placeholder — "phonenumber" ≠ "phone_number" | Placeholder Matching Case Insensitive |
| 31 | Edge case | Gherkin literal `007` vs body Constant(7) | Match via str(7) → "7" normalization — zero violations | Literal Matching Case Insensitive |
| 32 | Edge case | Gherkin literal `""` (empty string) vs body Constant("") | Match via str("") → "" normalization — zero violations | Literal Matching Case Insensitive |
| 33 | Edge case | Single-quoted `'<name>'` vs double-quoted `"<name>"` | Identical behavior: Placeholder extracted, no Literal double-capture | Quoted Placeholder Not Double Captured |
| 34 | Edge case | Body `x = +5` — UnaryOp(UAdd, Constant(5)) | Folded to 5 in body_constant_nodes, indistinguishable from `x = 5` | Negative Numbers Visible In Body |
| 35 | Edge case | Gherkin `"True"` (string) vs body `True` (boolean) | Match via str().lower() → both "true" — intentional collision | Literal Matching Case Insensitive (bool-string collision) |

---

## Pain Points

### PP-M1: Bare float not extracted as numeric literal — VERIFIED RESOLVED

**Severity:** — | **Status:** ✅ Resolved | **Iteration 1 severity:** High

The domain_spec `_extract_literals` regex has been changed from `^-?\d+$` to `^-?\d+(\.\d+)?$`. Walkthrough W14 already covered `-3.14` on the Test Discovery side (body constant collection via UnaryOp folding). With the regex fix, `-3.14` is now extractable on the Gherkin side as `Literal(value=-3.14, type=numeric)`. The feature file Scenario "negative float literal matches body constant" (line 106-111) is now valid — the scenario no longer passes vacuously.

**Verification:** domain_spec.md:216 rule 1 now specifies `^-?\d+(\.\d+)?$` with float tokens stored as `Literal(value=float(token))`. The `str().lower()` normalization in `check_pair` ensures `-3.14` matches body `Constant(-3.14)`.

### PP-M2: Empty quoted string `""` — VERIFIED RESOLVED

**Severity:** — | **Status:** ✅ Resolved | **Iteration 1 severity:** Medium

W32 confirms: `""` in Gherkin → `Literal(value="")`. Body `Constant("")` → `str("")` → `""`. Match confirmed — zero violations. Domain_spec.md:217 rule 2 explicitly documents this.

### PP-M3: Single-quoted placeholder `'<name>'` — VERIFIED RESOLVED

**Severity:** — | **Status:** ✅ Resolved | **Iteration 1 severity:** Medium

W33 confirms: `'<name>'` (single-quoted) behaves identically to `"<name>"` (double-quoted). `_extract_placeholders` extracts `<name>` regardless of quote style. `_extract_literals` filters `<...>` regardless of quote style. No Literal double-capture. Domain_spec.md:217 rule 2 explicitly states both `"..."` and `'...'` are handled identically.

### PP-M4: Numeric literal with leading zeros — VERIFIED RESOLVED

**Severity:** — | **Status:** ✅ Resolved | **Iteration 1 severity:** Low

W31 confirms: `007` → `int("007")` → `7`, `str(7)` → `"7"`. Body `Constant(7)` → `str(7)` → `"7"`. Match. Domain_spec.md:216 rule 1 documents that leading zeros are erased by `int()` conversion.

### PP-M5: Mixed case + underscores in placeholder name — VERIFIED RESOLVED

**Severity:** — | **Status:** ✅ Resolved | **Iteration 1 severity:** Low

W30 confirms: `<PhoneNumber>` vs `phone_number` → `"phonenumber"` ≠ `"phone_number"` after lowering → missing-placeholder violation. Expected behavior. Domain_spec.md:379 explicitly documents this.

### PP-M6: UnaryOp with UAdd `+5` — VERIFIED RESOLVED

**Severity:** — | **Status:** ✅ Resolved | **Iteration 1 severity:** Medium

W34 confirms: `x = +5` → `UnaryOp(UAdd(), Constant(5))` folded → exposes `5`. Indistinguishable from `x = 5`. Domain_spec.md:377 documents UAdd folding.

### PP-M7: Boolean `"True"`/`"False"` in Gherkin vs body bool — VERIFIED RESOLVED

**Severity:** — | **Status:** ✅ Resolved | **Iteration 1 severity:** Medium

W35 confirms: Gherkin `"True"` (string) matches body `True` (boolean) via `str().lower()` — both normalize to `"true"`. Intentional collision documented in domain_spec.md:477.

---

## Resolution Status

| Pain Point | Iteration 1 Status | Iteration 2 Status |
|------------|-------------------|-------------------|
| PP-M1: Bare float not extracted | **Resolved** — regex changed to `^-?\d+(\.\d+)?$` | **Verified** — regex fix covers float extraction; W14 already covered body-side |
| PP-M2: Empty quoted string `""` | **Resolved** — documented in domain_spec | **Verified** — W32 confirms match |
| PP-M3: Single-quoted placeholder `'<name>'` | **Resolved** — documented quote parity | **Verified** — W33 confirms identical behavior |
| PP-M4: Numeric literal with leading zeros | **Resolved** — documented in domain_spec | **Verified** — W31 confirms expected erasure |
| PP-M5: Mixed case + underscores in placeholder | **Resolved** — documented in domain_spec | **Verified** — W30 confirms mismatch |
| PP-M6: UnaryOp with UAdd `+5` | **Resolved** — documented in domain_spec | **Verified** — W34 confirms folding |
| PP-M7: Boolean `"True"`/`"False"` collision | **Resolved** — documented in domain_spec | **Verified** — W35 confirms intentional collision |

---

## E2E Completeness Walk (Re-verified)

All 7 rules from `case_insensitive_matching.feature` compose into a complete end-to-end journey. The float fix (PP-M1) closes the gap where the feature file Scenario "negative float literal matches body constant" was passing vacuously. The scenario now tests real Gherkin-side float extraction → body matching.

### Cross-Context Data Flow (Unchanged)

```
Gherkin step text
  → Feature Parsing (gherkin.py): parse_step → _extract_placeholders + _extract_literals
    → ScenarioInfo { placeholders: [Placeholder(Dog)], literals: [Literal("Rex"), Literal(-2010), Literal(-3.14)] }
    → CONFORMIST →
  → Consistency Checking (check.py): check_pair(si, ti)
    ← Test Discovery (discover.py): discover_tests → TestInfo { body_name_nodes: [dog, Dog], body_constant_nodes: ["rex", -2010, -3.14] }
    ← CONFORMIST
  → comparison: R5 (lowered Name set) + R6 (str().lower() set)
  → list[Violation] (empty = success)
```

### Edge Cases Now Covered (New in Iteration 2)

- W30: CamelCase placeholder vs snake_case body name → mismatch (expected)
- W31: Leading zeros in numeric literals → erased by `int()` (expected)
- W32: Empty quoted string → matches (expected)
- W33: Single-quoted placeholder → identical to double-quoted (expected)
- W34: `+5` UAdd folding → indistinguishable from bare `5` (expected)
- W35: String `"True"` vs boolean `True` → intentional collision (expected)

---

## Summary

| Metric | Iteration 1 | Iteration 2 |
|--------|------------|-------------|
| Walkthroughs performed | 29 | 35 (+6) |
| Rules discovered | 7 | 7 (no new rules) |
| Pain points found | 7 (PP-M1 through PP-M7) | 0 new |
| Pain points resolved | 7 | 7 (all verified) |
| Bugs verified resolved | 3 of 4 (#18, #19, #22) | 3 of 4 (unchanged) |
| Feature file | `docs/features/case_insensitive_matching.feature` | No changes needed |
| Simulation results | `.cache/sim/simulation_results_20260520T071043.md` | `.cache/sim/simulation_results_20260520T073818.md` |
| New walkthrough files | 58 (W01-W29 in/out) | 70 (W01-W35 in/out) |

**Verdict: PASS.** All 7 pain points from iteration 1 are verified resolved by concrete walkthroughs. Six additional edge cases (W30-W35) are covered and produce expected behavior. No new pain points discovered. The feature file requires no changes — all 7 existing rules cover the new edge cases. Cross-context consistency is maintained between `domain_spec.md` and `case_insensitive_matching.feature`.

### Reviewer Decision Criteria Assessment

| # | Criterion | Status | Detail |
|---|-----------|--------|--------|
| 1 | Zero unresolved pain points | ✅ PASS | All 7 PPs verified resolved by concrete walkthroughs |
| 2 | Entity coverage (all entities across all contexts) | ✅ PASS | All entities covered; 6 additional edge cases verified |
| 3 | Integration point coverage (success + failure per pair) | ✅ PASS | All integration points have success + failure walkthroughs |
| 4 | Quality attribute coverage | ✅ PASS | Correctness, Reliability, Simplicity verified |
| 5 | Rule quality (specific, testable, traceable, non-contradictory) | ✅ PASS | Float extraction now consistent; all edge cases documented |
| 6 | Cross-context consistency | ✅ PASS | No contradictions between domain_spec.md and feature files |

### Reviewer Notes

- **Stance:** Adversarial — actively searched for missed scenarios per [[architecture/reconciliation#concepts]]
- **Boundary check:** Verified cross-document relationships for all 3 bounded contexts
- **Re-simulation scope:** 5 targeted walkthroughs (W30-W35) covering all pain points from iteration 1
- **Float fix verification:** domain_spec regex `^-?\d+(\.\d+)?$` correctly enables bare float extraction; feature file Scenario line 106-111 now semantically valid (not vacuously passing)
- **No feature file changes needed:** Existing 7 rules cover all 5 new edge cases; no new rules, scenarios, or constraints required
