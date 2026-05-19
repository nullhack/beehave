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
| PP-1: Ambiguous no scenarios vs needs scenarios | Resolved | Added `EmptyRuleInfo` value object and `detect_empty_rules()` external contract to Feature Parsing. Stage Decision Tree priority 2 now calls `detect_empty_rules()` when `parse_feature()` returns `{}` to distinguish "no scenarios" from "needs scenarios". |
| PP-2: Feature stage derivation not explicit | Resolved | Added explicit invariant to Status Reporting: "Feature stage is determined by evaluating the Stage Decision Tree conditions in priority order (1 through 7). The first condition whose predicate is satisfied by any scenario determines the feature stage." |

---

## Review Verdict

**🔴 FAIL** — Review executed by R (Reviewer), adversarial stance per [[architecture/reconciliation#concepts]].

### Blocking Issues

| # | Pain Point | Severity | Blocking? | Detail |
|---|-----------|----------|-----------|--------|
| PP-1 | Ambiguous "no scenarios" vs "needs scenarios" | Medium | **YES** | Bilateral integration mismatch. Feature Parsing `parse_feature()` returns `{}` for both "no scenarios or rules" and "Rule with no scenarios" (domain_spec.md:185-186). Status Reporting Stage Decision Tree distinguishes priority 2 (`no scenarios`) from priority 3 (`needs scenarios`) but cannot detect this difference from `parse_feature()` output alone (Status Reporting is "pure presentation layer with no new parsing," domain_spec.md:439). The CONFORMIST pattern breaks: downstream cannot conform to upstream payload. |
| PP-2 | Feature stage derivation algorithm implicit | Low | **YES** | The Stage Decision Tree (domain_spec.md:525-533) lists conditions in priority order but does not state the invariant: "Feature stage is the highest-priority matching condition evaluated in order 1-7." Rule 8 ("Worst Scenario Wins") partially captures this but the domain spec itself lacks the explicit invariant. |

### Missed Scenarios (6 categories)

| # | Missing Entity/Behavior | Domain Spec Source | Why Absent from Simulation |
|---|------------------------|-------------------|---------------------------|
| M1 | **Exit codes (exit 0, 1, 2)** | domain_spec.md:516-519, Rule 12 in .feature | Status command exit code contract is specified in External Contracts and has 3 concrete scenarios in the .feature file, but zero simulation walkthroughs exercise exit code behavior. |
| M2 | **Orphaned test directories** | domain_spec.md:455,614 | StatusReport entity has `OrphanedDir 0:N` relationship. Error handling table specifies "Reported in orphaned_directories if --include-orphaned." No walkthrough. |
| M3 | **Cross-feature function name collisions** | domain_spec.md:456,592 | StatusReport entity has `Collision 0:N` relationship. Invariant: "name collisions do not affect stage" (domain_spec.md:620). No walkthrough. |
| M4 | **JSON output format** | domain_spec.md:567-603 | Complete JSON schema specified in Output Format section. The `--json` flag is listed in External Contract (domain_spec.md:512). No walkthrough verifies JSON structure, machine-readability, or `summary` counts. |
| M5 | **Test Discovery failure integration** | domain_spec.md:286-288 | Test Discovery error handling: "Python syntax error → returns empty dict; all scenarios unmapped." When this occurs during `beehave status`, the Status Reporting context must handle the empty dict. No walkthrough for this integration failure path. |
| M6 | **Fatal configuration error (exit 2)** | domain_spec.md:521,659 | CLI contract: "Exit 2: Fatal error (config missing, disk I/O failure)." Status Reporting preconditions: "Project has a valid Config" (domain_spec.md:521). Scenario exists in Rule 12 but no simulation walkthrough. |

### Quality Attribute Coverage

| Attribute | Priority | Stressed? | Evidence |
|-----------|----------|-----------|----------|
| **Correctness** (deterministic mapping) | Must | ⚠️ Undermined | W7-W8 show deterministic output, but PP-1 means the mapping from parse output to stage is underspecified — correct behavior for "needs scenarios" stage is undefined given current Feature Parsing contract. |
| **Reliability** (zero partial output) | Must | ❌ Not stressed | W1 shows error reporting for parse failure, but no walkthrough tests partial output scenario: "what happens if status processes 3 features, succeeds on 2, then encounters fatal I/O error on the 3rd?" The zero-partial-output guarantee is untested. Exit code walkthroughs (M1, M6) would stress this. |
| **Simplicity** (zero beehave imports) | Must | ➖ N/A | This quality attribute targets Code Generation context, not Status Reporting. Status Reporting correctly imports from beehave internally (gherkin, discover, check). Exempt for this simulation scope. |
| **Composability** (stable public API) | Should | ❌ Not stressed | The `--json` output IS the composability surface for external tooling. No walkthrough verifies JSON schema stability or backward-compatible API contract. |

### Rule Traceability

12 behavioral Rules in `status_command.feature`. **10 of 12** trace to simulation walkthroughs via provenance column.

| Rule | Walkthrough | Status |
|------|-------------|--------|
| Parse Error Captured as Stage | W1 | ✓ |
| Empty Features Report No Scenarios | W2 | ✓ |
| Rules Without Scenarios Detected | W3 | ⚠️ Affected by PP-1 |
| Unmapped Scenarios Derive Stage | W4 | ✓ |
| All Stubs Derive Stage | W5 | ✓ |
| Violations Derive Stage | W6 | ✓ |
| All Passing Derives Ok | W7 | ✓ |
| Worst Scenario Wins | W8 | ⚠️ Affected by PP-2 |
| Ok Feature Collapses in Output | W9 | ✓ |
| Tree Output Shows Rule Hierarchy | W10 | ✓ |
| Scenario Statuses Derive from Discovery | W4-W7 | ✓ |
| **Exit Codes Reflect Overall Status** | **NONE** | **❌ No provenance** |

### Cross-Context Consistency

| Integration | Pattern | Consistent? | Detail |
|-------------|---------|-------------|--------|
| Feature Parsing → Status Reporting | CONFORMIST | **❌ NO** | PP-1: `parse_feature()` payload cannot distinguish priority-2 from priority-3 conditions |
| Test Discovery → Status Reporting | CONFORMIST | ⚠️ Untested | Success path covered (W4-W10). Failure path (syntax error → empty dict) not simulated (M5) |
| Consistency Checking → Status Reporting | CONFORMIST | ✓ | `check_pair()` Violation list consumed as-is. W6-W7 verify. |

### Resolution Required

Before implementation can proceed:

1. **PP-1 must be resolved** — Options: (A) `parse_feature()` returns `has_rules` flag, (B) Status Reporting does lightweight AST pass, (C) richer parse result type. Stakeholder must decide.
2. **PP-2 must be resolved** — Add explicit invariant to domain_spec.md Status Reporting section: "Feature stage is determined by evaluating Stage Decision Tree conditions in priority order 1-7; the first condition whose predicate is satisfied determines the stage."
3. **Run fix-spec → re-simulate** — Address PP-1/PP-2, then re-simulate with the 6 missed scenario categories (M1-M6) as new walkthroughs.
4. **Verify quality attributes** — Add walkthroughs for Reliability (exit codes, partial output) and Composability (JSON schema validation).

### Simulation Discrepancy Note

Simulation results summary claims "3 happy paths, 4 edge cases, 3 error paths" but walkthrough evidence files show 5 happy paths (W4,W5,W7,W9,W10), 3 edge cases (W2,W3,W8), and 2 error paths (W1,W6). Reconcile counts in next simulation iteration.
