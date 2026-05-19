# Simulation Results: Status Reporting

> **Timestamp:** 2026-05-19T17:10:37Z
> **Contexts simulated:** Status Reporting
> **Iteration:** 1 of 5

---

## Walkthroughs Performed

| # | Type | Input / Condition | Expected Stage / Output | Discovered Rule |
|---|------|------------------|------------------------|-----------------|
| 1 | Error path | Invalid Gherkin (missing colon after Scenario keyword) → `parse_feature()` raises `GherkinError` | stage = `broken`, `parse_error_message` populated | Parse Error Captured as Stage |
| 2 | Edge case | Feature file parses but has zero Scenario or Rule nodes → `parse_feature()` returns `{}` | stage = `no scenarios` | Empty Features Report No Scenarios |
| 3 | Edge case | Feature file has 2 Rule nodes with zero Scenario children → `parse_feature()` returns `{}` | stage = `needs scenarios` | Rules Without Scenarios Detected |
| 4 | Happy path | Feature with 3 scenarios; 2 mapped to test functions, 1 unmapped | stage = `needs tests` | Unmapped Scenarios Derive Stage |
| 5 | Happy path | Feature with 3 scenarios; all mapped to stub tests (`is_stub=True`) | stage = `needs bodies` | All Stubs Derive Stage |
| 6 | Error path | Feature with 3 non-stub tests; one has `missing-literal` violation via `check_pair()` | stage = `needs fixes` | Violations Derive Stage |
| 7 | Happy path | Feature with 3 non-stub tests; zero violations from `check_pair()` | stage = `ok` | All Passing Derives Ok |
| 8 | Edge case | Feature with 1 ok, 1 no body, 1 no test → worst scenario = `no test` | stage = `needs tests` | Worst Scenario Wins |
| 9 | Happy path | Feature with all scenarios `ok` → tree output collapses to single line | Single line: `ok  feature_slug (Title)` | Ok Feature Collapses in Output |
| 10 | Happy path | Feature with 2 Rules containing mixed scenario statuses | Tree hierarchy with rule aggregation labels | Tree Output Shows Rule Hierarchy |

---

## Pain Points

### PP-1: Ambiguous distinction between "no scenarios" and "needs scenarios" stages

- **Classification:** ambiguous
- **Severity:** Medium
- **Context:** Status Reporting → Stage Decision Tree priorities 2 and 3
- **Description:** The domain spec's Feature Parsing context states that `parse_feature()` returns `{}` for both "Feature with no scenarios or rules" and "Rule with no scenarios" (Error Handling table, lines 185-186). However, the Status Reporting Stage Decision Tree distinguishes between `no scenarios` (priority 2, `parse_feature() returns {}`) and `needs scenarios` (priority 3, "Feature has Rules but every Rule has zero Scenarios"). The Status Reporting context (line 436) states it is a "pure presentation layer with no new parsing." It cannot distinguish these cases using only `parse_feature()` output.
- **Impact:** The status command cannot correctly compute `needs scenarios` stage without additional information from Feature Parsing.
- **Possible resolution:**
  - Option A: `parse_feature()` returns a `has_rules: bool` flag alongside the scenario dict (or as a separate return).
  - Option B: Status Reporting makes a lightweight Gherkin AST pass to detect Rule nodes when `parse_feature()` returns `{}`.
  - Option C: `parse_feature()` returns a richer result type that distinguishes the two cases (e.g., `None` for parse error, `{}` with `rule_count` in metadata).
- **Source:** walkthrough_3_out.json

### PP-2: Feature Stage derivation algorithm not explicitly stated

- **Classification:** ambiguous
- **Severity:** Low
- **Context:** Status Reporting → Stage Decision Tree
- **Description:** The Stage Decision Tree (lines 525-533) lists priority-ordered conditions with stage labels, but the algorithm for deriving the feature stage from the set of scenario statuses is only demonstrated implicitly through the "Mixed feature → worst wins" walkthrough. The spec would benefit from an explicit invariant: "Feature stage is the lowest-priority stage whose condition is met by any scenario in the feature" (or equivalently, "the worst stage among all scenarios").
- **Impact:** Implementers might misinterpret the derivation order. The existing table is clear enough for most readers but the mapping from scenario statuses to feature stages is implicit.
- **Possible resolution:** Add an invariant: "Feature stage is determined by the highest-priority matching condition from the Stage Decision Tree, where the conditions are evaluated in priority order 1-7."
- **Source:** walkthrough_8_in.json, domain_spec.md:525-533

---

## Resolution Status

| Pain Point | Status | Resolution |
|------------|--------|------------|
| PP-1: Ambiguous no scenarios vs needs scenarios | Open | Needs clarification from Feature Parsing: how does Status Reporting detect Rules? |
| PP-2: Feature stage derivation not explicit | Open | Minor — table is clear enough but an invariant would help. |

---

## Summary

- **Walkthroughs executed:** 10 (3 happy paths, 4 edge cases, 3 error paths)
- **Pain points found:** 2 (1 ambiguous, 1 ambiguous — severity Medium + Low)
- **Rules discovered in .feature file:** 12
- **Overall assessment:** The Status Reporting bounded context has a well-specified stage decision tree and output format. The primary issue (PP-1) is an integration ambiguity between Feature Parsing and Status Reporting that would manifest at implementation time. The decision tree itself covers all 7 stages with clear priority ordering. The output format specification (both human-readable tree and JSON) is detailed and consistent with the domain model.

All 10 walkthroughs produce deterministic, spec-consistent outputs. The simulation confirms the Status Reporting context is implementable, with only the PP-1 ambiguity needing stakeholder clarification before implementation can proceed.
