# Simulation Results: Title Validation

> **Timestamp:** 2026-05-19T18:56:38Z
> **Contexts simulated:** Feature Parsing (Title Validation)
> **Iteration:** 1 of 5

---

## Walkthroughs Performed

| # | Type | Input / Condition | Expected Output | Discovered Rule |
|---|------|------------------|----------------|-----------------|
| 1 | Happy path | Single .feature file: Feature "Hive Activity" (2w), Rule "Hive defense" (2w), Scenario "guard bee inspects visitor" (4w) — all valid charset, word count 2-6, unique | Empty violations list | Valid Titles Produce No Violations |
| 2 | Happy path | Two .feature files with globally unique titles across all three types (Feature "Hive Activity" / "Comb Construction") | Empty violations list | Valid Titles Produce No Violations |
| 3 | Edge case | Feature title "Minimal Title" = 2 words exactly (lower word count boundary) | Empty violations list — passes word count | Valid Titles Produce No Violations |
| 4 | Edge case | Scenario title "worker bee deposits nectar into wax cell" = 6 words exactly (upper boundary) | Empty violations list — passes word count | Valid Titles Produce No Violations |
| 5 | Edge case | Feature title "Activity" = 1 word (below minimum) | invalid-feature-title violation | Title Word Count Is Validated |
| 6 | Edge case | Rule title "the guards respond to all unknown visitor bees" = 7 words (above maximum) | invalid-rule-title violation | Title Word Count Is Validated |
| 7 | Edge case | Scenario title "" = 0 words (empty after keyword strip) | invalid-scenario-title violation | Title Word Count Is Validated |
| 8 | Edge case | Feature title "Hive-Activity" contains hyphen (-) — not in `[\w\s]+` | invalid-feature-title violation | Title Charset Is Validated |
| 9 | Edge case | Rule title "Guard.Inspection" contains period (.) — not in `[\w\s]+` | invalid-rule-title violation | Title Charset Is Validated |
| 10 | Edge case | Scenario title "guard_bee_inspects" contains underscore (_) — pain point: `\w` includes underscore in Python regex | invalid-scenario-title violation (assumes spec intent is letters/digits/spaces only) | Title Charset Is Validated |
| 11 | Edge case | Two features: "Hive Activity" vs "hive activity" — case-insensitive duplicate | Two duplicate-feature-title violations (one per file) | Duplicate Titles Are Detected |
| 12 | Edge case | Rule title "Hive Activity" matches Feature title "Hive Activity" — cross-type duplicate | duplicate-rule-title violation | Duplicate Titles Are Detected |
| 13 | Edge case | Scenario title "guard inspection" matches Feature title "Guard Inspection" (case-insensitive) — cross-type duplicate | duplicate-scenario-title violation | Duplicate Titles Are Detected |
| 14 | Edge case | Scenario title "Foraging Patterns" matches Rule title "Foraging Patterns" — cross-type duplicate | duplicate-scenario-title violation | Duplicate Titles Are Detected |
| 15 | Edge case | Two scenarios in same file: "guard bee inspects visitor" and "Guard Bee Inspects Visitor" (case-insensitive) | Two duplicate-scenario-title violations | Duplicate Titles Are Detected |
| 16 | Edge case | Feature title "Config: Strategy Defaults" — colon in text after keyword strip. Pain point: colons part of title text per spec but not in charset | invalid-feature-title violation (colon fails `[\w\s]+`) | Title Charset Is Validated |
| 17 | Error path | One valid file + one broken Gherkin file (missing colon syntax error) | GherkinError raised — pain point: zero partial output vs partial results? | (none — error path) |
| 18 | Edge case | File "mixed_issues.feature" with hyphen Feature title + duplicate Rule title; "other.feature" with duplicate Feature title | 3 violations: 1 invalid-feature-title, 1 duplicate-rule-title, 1 duplicate-feature-title | Duplicate Titles Are Detected |
| 19 | Integration | check_all() with bad Feature title (hyphen) + unmapped scenario | Combined title + scenario violations in check_all output; title violations are non-warning errors | Title Violations Included In Check |
| 20 | Integration | generate_stubs() pre-flight — one file has 7-word Feature title while another has valid titles | SystemExit(1); zero stubs generated for any feature; all-or-nothing invariant | Title Validation Blocks Generation |

---

## Pain Points

### PP-1: `[\w\s]+` regex ambiguity — underscore behavior

- **Classification:** ambiguous
- **Walkthrough:** W10
- **Detail:** The domain spec (line 95, 220) says title charset is `[\w\s]+` and describes it as "letters/digits/spaces only" (line 95) and "Non-empty, letters/digits/spaces only". In Python's `re` module, `\w` matches `[a-zA-Z0-9_]` — including underscore. The plain-language description "letters/digits/spaces only" excludes underscore, but the regex `[\w\s]+` would allow it. The Gherkin knowledge file ([[requirements/gherkin#key-takeaways]]) explicitly states: "Titles must contain ONLY Unicode letters, digits, and spaces — no hyphens, periods, underscores, or special characters." This is a contradiction between the regex notation and the plain-language spec.
- **Impact:** An implementer using `re.match(r'[\w\s]+$', ...)` would allow underscores through, contradicting the domain spec's plain-language requirement. An implementer reading the plain-language description would block underscores but deviate from the `[\w\s]+` regex pattern.
- **Suggested resolution:** Either (a) change the regex to `[\p{L}\p{N}\s]+` (Unicode-aware letters and digits only, no underscores) and update the notation in the spec, or (b) acknowledge that underscores are intentionally allowed by `\w` and update the plain-language description to say "letters, digits, underscores, and spaces".

### PP-2: Colon in title text contradicts charset constraint

- **Classification:** contradictory
- **Walkthrough:** W16
- **Detail:** Domain spec line 253 states: "colons in title text are part of the title." However, colon (`:`) is punctuation and is not in `[\w\s]+`. If colons are part of the title text, they will fail charset validation. This creates a direct contradiction: the spec simultaneously says colons are allowed (as part of title text) and disallowed (by the charset regex).
- **Impact:** A Feature title like "Config: Strategy Defaults" where the colon appears after the Gherkin keyword strip would fail charset validation, but the spec suggests it should be valid. The implementer has no clear guidance.
- **Suggested resolution:** Either (a) update the charset to allow colons: `[\w\s:]+` and explicitly list colon as a permitted character, or (b) state that colons are not valid in title text and update line 253 to say "colons in title text are a parse error."

### PP-3: validate_all_titles error behavior with partial file scanning

- **Classification:** ambiguous
- **Walkthrough:** W17
- **Detail:** Domain spec line 263 says `validate_all_titles()` "makes a single pass over all .feature files." When file 2 of 3 has a Gherkin syntax error, the spec is ambiguous about whether the function returns violations from file 1 (already scanned) or raises GherkinError immediately with zero output. The contract (line 218) says "GherkinError caught by caller" — suggesting the caller decides what to do. But the Reliability quality attribute mandates "Zero partial output on failure" — suggesting no violations should be returned when a parse error occurs.
- **Impact:** Callers (check_all, generate_stubs) need to know whether they might receive both violations and an error, or always exactly one result. The current spec is ambiguous.
- **Suggested resolution:** State explicitly: "If any .feature file fails to parse, validate_all_titles raises GherkinError immediately without returning any violations — zero partial output."

---

## Resolution Status

| Pain Point | Status | Resolution |
|------------|--------|------------|
| PP-1: `[\w\s]+` regex ambiguity | Open | Needs spec clarification — either update regex or update plain-language description |
| PP-2: Colon in title text vs charset | Open | Needs spec clarification — colon must be either allowed or disallowed, not both |
| PP-3: Partial failure error behavior | Open | Needs spec clarification — define zero-partial-output behavior explicitly |

---

## E2E Completeness Walk

Stringing all 6 rules from `title_validation.feature` into an end-to-end validation journey:

1. **Entry:** `validate_all_titles(config)` is called by `check_all()` or `generate_stubs(pre-flight)`
2. **Config read:** `config.features_dir` provides the directory to scan for `.feature` files
3. **File enumeration:** Discover all `.feature` files in `features_dir`
4. **Per-file lightweight AST traversal:**
   - Parse each `.feature` via gherkin-official AST
   - **Parse error** → `GherkinError` raised immediately (zero partial output) → **Rule: (none — error path, PP-3 ambiguous)**
   - Extract Feature title, Rule titles, Scenario/Scenario Outline titles
5. **Per-title validation:**
   - **Charset check:** `[\w\s]+` regex match → **Rule: Title Charset Is Validated** ✓
     - Hyphen → invalid-feature-title (W8)
     - Period → invalid-rule-title (W9)
     - Underscore → invalid-scenario-title (W10, PP-1)
     - Colon → invalid-feature-title (W16, PP-2 — contradictory)
   - **Word count check:** Split on whitespace, count 2-6 words → **Rule: Title Word Count Is Validated** ✓
     - 1 word → violation (W5)
     - 7 words → violation (W6)
     - Empty → violation (W7)
   - **All pass** → no charset/word count violations → **Rule: Valid Titles Produce No Violations** ✓ (W1-W4)
6. **Global uniqueness check** (after all files scanned):
   - Case-insensitive comparison across Feature, Rule, Scenario pools → **Rule: Duplicate Titles Are Detected** ✓
     - Feature vs Feature → duplicate-feature-title (W11)
     - Rule vs Feature → duplicate-rule-title (W12)
     - Scenario vs Feature → duplicate-scenario-title (W13)
     - Scenario vs Rule → duplicate-scenario-title (W14)
     - Scenario vs Scenario → duplicate-scenario-title (W15)
     - Mixed violations → multiple violation types in one pass (W18)
7. **Check integration:** `check_all()` appends title violations → **Rule: Title Violations Included In Check** ✓ (W19)
   - Title violations are non-warning errors, contribute to exit code 1
8. **Generate pre-flight:** `generate_stubs()` calls validate_all_titles first → **Rule: Title Validation Blocks Generation** ✓ (W20)
   - Any violation → SystemExit(1), zero stubs written
   - All-or-nothing: one bad title blocks generation for ALL features

### Completeness Assessment

| Criterion | Status | Detail |
|-----------|--------|--------|
| Happy-path flow: validate_all_titles → output | ✅ Complete | W1-W4 cover valid titles producing empty violations list across single and multi-file scenarios. |
| External Contract rules → fixture detail | ✅ Complete | Violation shape (path, line, error_type, message, is_warning) defined. All 6 violation types covered. Contract input (config) and output (list[Violation]) clear. |
| Composed rules → working validation | ⚠️ Blocked by PP-1, PP-2, PP-3 | PP-1 (underscore) and PP-2 (colon) prevent deterministic charset implementation. PP-3 prevents caller from knowing error contract. |
| Cross-context flows complete | ✅ Complete | Feature Parsing→Consistency Checking (W19): title violations in check_all. Feature Parsing→Code Generation (W20): pre-flight blocks generation. Both CONFORMIST, payloads match. |
| Missing E2E steps | PP-3: Error path undefined | No walkthrough can simulate what happens when file N of M fails — zero output vs partial? |

---

## Quality Attribute Coverage

| Attribute | Priority | Stressed? | Evidence |
|-----------|----------|-----------|----------|
| **Correctness** (deterministic mapping) | Must | ✅ | All validation rules are deterministic: given the same feature files, the same violations are always produced. W1-W2 verify deterministic empty lists; W5-W15 verify deterministic violation production. |
| **Reliability** (zero partial output) | Must | ⚠️ Partially stressed | W20 verifies generate_stubs zero-partial-output: violation pre-flight → no files created. W17 is ambiguous (PP-3) — error behavior during multi-file scan is undefined. |
| **Simplicity** (zero beehave imports) | Must | ➖ N/A | Targets Code Generation context, not Feature Parsing. Feature Parsing imports gherkin-official internally as expected. |
| **Composability** (stable public API) | Should | ✅ | Violation structure (domain_spec.md lines 121-128) is stable; caller API is `validate_all_titles(config) -> list[Violation]`. W19/W20 verify composability from two different callers. |

---

## Rule Traceability

All 6 Rules in `title_validation.feature` traced to simulation walkthroughs.

| Rule | Walkthrough(s) | Status |
|------|---------------|--------|
| Valid Titles Produce No Violations | W1, W2, W3, W4 | ✓ |
| Title Charset Is Validated | W8, W9, W10, W16 | ⚠️ (PP-1, PP-2) |
| Title Word Count Is Validated | W5, W6, W7 | ✓ |
| Duplicate Titles Are Detected | W11, W12, W13, W14, W15, W18 | ✓ |
| Title Violations Included In Check | W19 | ✓ |
| Title Validation Blocks Generation | W20 | ✓ |

---

## Cross-Context Consistency

| Integration | Pattern | Consistent? | Detail |
|-------------|---------|-------------|--------|
| Feature Parsing → Consistency Checking (Title Validation) | CONFORMIST | ✅ | validate_all_titles returns list[Violation]; check_all appends to result. W19 verified combined output. |
| Feature Parsing → Code Generation (Title Validation Pre-Flight) | CONFORMIST | ✅ | validate_all_titles called before any file writes; non-empty result → SystemExit(1). W20 verified all-or-nothing invariant. |
| Configuration → Feature Parsing | OHS | ✅ | Config provides features_dir. W1-W20 all assume features_dir is set via config. |

---

## Summary

**Verdict: ⚠️ PASS WITH PAIN POINTS** — 3 pain points identified, all require stakeholder clarification before implementation.

### Decision Criteria

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | Zero unresolved pain points | ❌ | 3 open pain points: PP-1 (underscore regex ambiguity), PP-2 (colon contradiction), PP-3 (error behavior ambiguity). All need spec-level clarification. |
| 2 | Entity coverage | ✅ | Violation entity (all 6 error_type values) covered. ScenarioInfo, Config, Feature, Rule, Scenario titles all exercised. |
| 3 | Integration point coverage | ✅ | Feature Parsing→Consistency Checking (W19) and Feature Parsing→Code Generation (W20) both covered with success and failure scenarios. |
| 4 | Quality attribute coverage | ⚠️ | Correctness stressed (W1-W18). Reliability partially stressed (W20, but PP-3 blocks W17). Simplicity N/A. Composability stressed (W19-W20). |
| 5 | Rule quality (6 rules) | ✅ | All 6 rules are BDD-testable with concrete Example scenarios. Traceable to walkthroughs. No contradictions between rules. Word count and charset rules fully covered. |
| 6 | Cross-context consistency | ✅ | Both integration points (check_all, generate_stubs pre-flight) have matching payload shapes. CONFORMIST patterns verified. |

### Counts

- Total walkthroughs: 20
- Rules with provenance: 6/6 (100%)
- Pain points: 3 (all open)
- Pain point categories: 1 ambiguous, 1 contradictory, 1 ambiguous

### Non-Blocking Observations

- The Feature feature file title "Title Validation" has 2 words ✓, unique across all .feature files ✓, and uses only letters and spaces ✓.
- All Rule titles are 2-6 words and unique within the feature file.
- The existing `hive_activity.feature` uses `Scenario:` and `Scenario Outline:` keywords. The title_validation.feature follows the same convention for consistency within the project, even though [[requirements/gherkin]] recommends `Example:`.
