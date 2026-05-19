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
| PP-1: `[\w\s]+` regex ambiguity | **Resolved** | Allow underscores. Regex `[\w\s]+` is correct — `_` is valid in titles. Stakeholder decision: 2026-05-19. |
| PP-2: Colon in title text vs charset | **Resolved** | Reject colons. Colons in title text are invalid — current charset `[\w\s]+` is correct. Stakeholder decision: 2026-05-19. |
| PP-3: Partial failure error behavior | **Resolved** | Zero partial output. If GherkinError occurs mid-scan, `validate_all_titles` raises immediately — no violations returned. Stakeholder decision: 2026-05-19. |

### Artifact Update Tasks (for fix-spec)

The following artifacts contain stale content that contradicts the resolved positions above. These are NOT new pain points — they are natural consequences of the stakeholder resolutions and must be updated in fix-spec:

| Artifact | Location | Issue | Resolution Needed |
|----------|----------|-------|-------------------|
| `title_validation.feature` | Lines 93-98 | Scenario `scenario title contains an underscore` expects `invalid-scenario-title` for `guard_bee_inspects` | Remove this Scenario or invert it (underscore → no violation). With PP-1 resolved, underscores are valid. |
| `title_validation.feature` | Lines 72-78 | Rule "Title Charset Is Validated" description says "Unicode letters, digits, and spaces only" | Update to "Unicode letters, digits, underscores, and spaces only" to match resolved PP-1 position. |
| `domain_spec.md` | Line 95 | ScenarioInfo.title constraint: "Non-empty, letters/digits/spaces only" | Update to "Non-empty, letters/digits/underscores/spaces only" or equivalent. |
| `domain_spec.md` | Line 220 | Charset rule says `[\w\s]+` but plain-language description needs alignment | Clarify that `\w` intentionally includes underscore — update surrounding prose. |
| `domain_spec.md` | Line 253 | "colons in title text are part of the title" | Remove or invert — colons are now explicitly invalid (PP-2 resolved). |

---

## E2E Completeness Walk

Stringing all 6 rules from `title_validation.feature` into an end-to-end validation journey:

1. **Entry:** `validate_all_titles(config)` is called by `check_all()` or `generate_stubs(pre-flight)`
2. **Config read:** `config.features_dir` provides the directory to scan for `.feature` files
3. **File enumeration:** Discover all `.feature` files in `features_dir`
4. **Per-file lightweight AST traversal:**
   - Parse each `.feature` via gherkin-official AST
    - **Parse error** → `GherkinError` raised immediately (zero partial output) → **(PP-3 resolved: zero partial output, consistent with Reliability)**
    - Extract Feature title, Rule titles, Scenario/Scenario Outline titles
 5. **Per-title validation:**
    - **Charset check:** `[\w\s]+` regex match → **Rule: Title Charset Is Validated** ✓
      - Hyphen → invalid-feature-title (W8)
      - Period → invalid-rule-title (W9)
      - Underscore → valid (W10, PP-1 resolved: underscore is allowed by `\w`)
      - Colon → invalid-feature-title (W16, PP-2 resolved: colons rejected)
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
| Composed rules → working validation | ✅ Complete | PP-1/PP-2/PP-3 all resolved by stakeholder. Charset: underscores allowed, colons rejected. Error behavior: zero partial output on GherkinError. |
| Cross-context flows complete | ✅ Complete | Feature Parsing→Consistency Checking (W19): title violations in check_all. Feature Parsing→Code Generation (W20): pre-flight blocks generation. Both CONFORMIST, payloads match. |
| Missing E2E steps | ✅ None | PP-3 resolved: GherkinError → immediate raise, zero partial output. Error path is now defined. |

### New Reviewer Observations (non-blocking)

These are NOT pain points and do NOT block PASS. They are observations for fix-spec attention:

| Obs# | Category | Detail |
|------|----------|--------|
| OBS-1 | Missing walkthrough | No walkthrough tests a Scenario Outline title specifically. The .feature file Rules reference "Scenario/Scenario Outline" but all title walkthroughs use `Scenario:` keyword. Keyword stripping is identical for both (`Scenario Outline:` → strip → title), so risk is low. |
| OBS-2 | Unicode regex gap | `domain_spec.md` line 95 says "Unicode letters" and [[requirements/gherkin]] says "Unicode letters, digits, and spaces." But `[\w\s]+` in Python's default `re` mode matches only ASCII `[a-zA-Z0-9_\s]`. Accented characters (é, ñ, ü) would fail charset despite being "Unicode letters." No walkthrough tested non-ASCII characters. Consider either adding `re.UNICODE` flag or narrowing charset claim to ASCII. |

---

## Quality Attribute Coverage

| Attribute | Priority | Stressed? | Evidence |
|-----------|----------|-----------|----------|
| **Correctness** (deterministic mapping) | Must | ✅ | All validation rules are deterministic: given the same feature files, the same violations are always produced. W1-W2 verify deterministic empty lists; W5-W15 verify deterministic violation production. |
| **Reliability** (zero partial output) | Must | ✅ | W17: GherkinError→immediate raise, zero violations (PP-3 resolved). W20: pre-flight failure → SystemExit(1), zero stubs. Fully stressed. |
| **Simplicity** (zero beehave imports) | Must | ➖ N/A | Targets Code Generation context, not Feature Parsing. Feature Parsing imports gherkin-official internally as expected. |
| **Composability** (stable public API) | Should | ✅ | Violation structure (domain_spec.md lines 121-128) is stable; caller API is `validate_all_titles(config) -> list[Violation]`. W19/W20 verify composability from two different callers. |

---

## Rule Traceability

All 6 Rules in `title_validation.feature` traced to simulation walkthroughs.

| Rule | Walkthrough(s) | Status |
|------|---------------|--------|
| Valid Titles Produce No Violations | W1, W2, W3, W4 | ✓ |
| Title Charset Is Validated | W8, W9, W10, W16 | ⚠️ PP-1/PP-2 resolved; artifact updates needed (.feature W10 Scenario contradicts resolved underscore position; domain_spec lines 95, 253) |
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

**Verdict: ✅ PASS** — Adversarial review complete. All 3 original pain points resolved by stakeholder. All 6 reviewer decision criteria met. 2 non-blocking observations recorded for fix-spec attention.

### Review Authority

| Field | Value |
|-------|-------|
| Reviewer | R (independent, not the SA who simulated) |
| Review timestamp | 2026-05-19T19:30:00Z |
| Review iteration | 1 of 5 |
| Stance | Adversarial — actively searched for missed scenarios, invalid pain points, cross-document contradictions |

### Decision Criteria

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | Zero unresolved pain points | ✅ | PP-1, PP-2, PP-3 all resolved by stakeholder (2026-05-19). 0 unresolved. |
| 2 | Entity coverage | ✅ | Violation (6 error_types), Config, Feature/Rule/Scenario titles all exercised across happy/edge/error paths. Minor gap: no Scenario Outline title walkthrough (OBS-1, low risk). |
| 3 | Integration point coverage | ✅ | Feature Parsing→Consistency Checking and Feature Parsing→Code Generation both covered with success and failure scenarios. GherkinError propagation architecturally consistent. |
| 4 | Quality attribute coverage | ✅ | Correctness: deterministic mapping (W1-W18). Reliability: zero partial output (W17, W20). Simplicity: N/A. All Must-priority attributes stressed. |
| 5 | Rule quality (6 rules) | ✅ | All 6 rules specific, BDD-testable, traceable to walkthroughs (100% provenance), no rule-to-rule contradictions. ⚠️ Rule "Title Charset Is Validated" Scenario W10 needs update to match PP-1 resolution (artifact stale, not a new pain point). |
| 6 | Cross-context consistency | ✅ | Both integration points have matching CONFORMIST payloads. Bilateral contracts verified. |

### Cross-Document Consistency (Reconciliation Check)

| Check | Documents | Status | Detail |
|-------|-----------|--------|--------|
| domain_spec ↔ glossary | Feature/Rule/Scenario/Scenario Outline terms | ✅ | Glossary definitions (lines 78, 160, 172, 184) align with domain_spec usage. |
| domain_spec ↔ feature | validate_all_titles contract, error types, charset, word count | ⚠️ | Feature file W10 Scenario (underscore→violation) contradicts PP-1 resolution. domain_spec line 253 contradicts PP-2 resolution. Fix-spec will update both. |
| glossary ↔ feature | "Titles must contain ONLY" vs resolved position | ⚠️ | Glossary for Feature (line 78) says "globally-unique title" but charset is in domain_spec. [[requirements/gherkin]] says "Unicode letters, digits, and spaces only" — needs update for underscores per PP-1. |
| product_definition ↔ scope | Title validation within beehave scope | ✅ | Title validation is a beehave check, not a test runner/framework — within scope. |

### Counts

- Total walkthroughs: 20
- Rules with provenance: 6/6 (100%)
- Pain points: 3 (all resolved by stakeholder)
- New observations: 2 (non-blocking, for fix-spec attention)
- E2E completeness: 4/4 criteria passed (was 3/4 with PP-3 blocking; now 4/4)

### Non-Blocking Observations (from original simulation, still valid)

- The Feature feature file title "Title Validation" has 2 words ✓, unique across all .feature files ✓, and uses only letters and spaces ✓.
- All Rule titles are 2-6 words and unique within the feature file.
- The existing `hive_activity.feature` uses `Scenario:` and `Scenario Outline:` keywords. The title_validation.feature follows the same convention for consistency within the project, even though [[requirements/gherkin]] recommends `Example:`.

### Artifact Update Tasks for Fix-Spec

The following must be updated in fix-spec to align artifacts with stakeholder resolutions:

1. **`title_validation.feature` lines 93-98**: Remove or invert Scenario "scenario title contains an underscore" — underscore is now valid.
2. **`title_validation.feature` lines 72-78**: Update Rule description to say "Unicode letters, digits, underscores, and spaces only."
3. **`domain_spec.md` line 95**: Update ScenarioInfo.title constraint to allow underscores.
4. **`domain_spec.md` line 220**: Update charset prose to clarify `\w` intentionally includes underscore.
5. **`domain_spec.md` line 253**: Remove or invert "colons in title text are part of the title."
6. **Consider OBS-1**: Add Scenario Outline title variant to one existing walkthrough or create a new W21.
7. **Consider OBS-2**: Clarify whether `\w` matches Unicode or ASCII letters (add `re.UNICODE` flag or narrow claim).
