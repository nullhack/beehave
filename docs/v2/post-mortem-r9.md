# beehave v2 Spec Post-Mortem — Round 9 (Adversarial Walk-Through)

> Mental adversarial walk-through of the complete v2 spec after 8 prior rounds
> (60+ issues resolved). Focused on CLI end-to-end flows, cache lifecycle,
> vocabulary enforcement edge cases, background composition, decorator
> resolution, and error recovery. Reviewed by System Architect (SA subagent).

---

## PP-V2-R9-1: `max_examples` default contradicts across sections ✅ RESOLVED

**Severity:** High
**Location:** Hypothesis Binding (line 109) vs Configuration (lines 320, 620)

The Hypothesis Binding section stated "Default: 100" while Configuration said
"Default: 1". R8-M4 resolved the default as 1 but only updated Configuration,
not the Hypothesis Binding section. Two implementers reading different sections
would build compliant-but-incompatible implementations.

**Resolution:** Changed line 109 from "Default: 100." to "Default: 1
(configurable via `max_examples` in `[tool.beehave]`)."

---

## PP-V2-R9-2: `@And`/`@But` inheritance scope contradicts — line 44 vs line 99 ✅ RESOLVED

**Severity:** Medium
**Location:** Step Decorators (line 44) vs Background (line 99)

Line 44 said inheritance is scoped "on the same function." Line 99 (updated in
R6-07) said "in the combined list" (background + scenario). These produce
different results when a scenario's first decorator is `@And` preceded by a
background `@Given`.

**Resolution:** Updated line 44 to "in the combined step list (background +
scenario)" — consistent with line 99 and R6-07's resolution.

---

## PP-V2-R9-3: Background function names break on special chars in Feature/Rule titles ✅ RESOLVED

**Severity:** Medium
**Location:** generate command — Background stubs paragraph (line 520)

Background function names derive from Feature/Rule titles using space→underscore
conversion. But Feature and Rule titles had no character restriction — titles
like `"E-Commerce"` or `"API v2.0"` produce `background_e-commerce` or
`background_api_v2.0` — invalid Python identifiers. `generate` would create
files with syntax errors.

**Resolution:** Extended the title format rule (line 15) to apply the same
character restriction (Unicode letters, digits, spaces only) to Feature and
Rule titles, not just Scenario titles. This ensures all derived function names
are valid Python identifiers.

---

## PP-V2-R9-4: `generate` append behavior undefined ✅ RESOLVED

**Severity:** Medium
**Location:** generate command (lines 494–521)

The spec described `generate` for new files but never defined what happens when
appending to an existing file. Two gaps: (1) import management — second run
needs `Example` in imports when a Scenario Outline is added, (2) background
re-emission — re-emitting `background_bank()` on every run creates duplicate
definitions.

**Resolution:** Added "Appending to existing files" paragraph: `generate`
updates imports (adds new symbols) and emits only new test function stubs.
Background functions are emitted only on first file creation; subsequent runs
reuse existing functions by name reference.

---

## PP-V2-R9-5: `clean` doesn't remove unreferenced background functions ✅ RESOLVED

**Severity:** Low
**Location:** Clean Command (line 477–478)

When all scenarios in a feature are deleted, `clean` removes orphan test
functions but leaves the background function as dead code. If the user later
re-adds scenarios with modified background steps, the stale background function
causes vocabulary enforcement failures.

**Resolution:** Extended `clean` to also remove background functions no longer
referenced by any `@Background` decorator in the same file.

---

## PP-V2-R9-6: Rule title uniqueness constraint not stated ✅ RESOLVED

**Severity:** Low
**Location:** Background rules (line 93–104), Cache structure

The cache stores rules as a dict keyed by rule title. Duplicate rule titles in
the same feature would silently overwrite — all scenarios from the first rule
lost with no error. The spec required globally unique Scenario titles but never
addressed Rule titles.

**Resolution:** Added rule 11: "Rule titles must be unique within a Feature.
Duplicate rule titles → parse error."

---

## Summary

| Status | Count | IDs |
|--------|-------|-----|
| ✅ Resolved | 6 | R9-1, R9-2, R9-3, R9-4, R9-5, R9-6 |
| ⬇️ Dropped | 0 | |
| ❌ Pending | 0 | |
| **Total** | **6** | |

### Spec Changes

| Change | Source |
|--------|--------|
| `max_examples` default: line 109 changed from 100 to 1 | R9-1 |
| `@And`/`@But` inheritance: "on the same function" → "in the combined step list" | R9-2 |
| Feature/Rule titles: same character restriction as Scenario titles | R9-3 |
| `generate` append: updates imports, emits only new stubs, reuses existing backgrounds | R9-4 |
| `clean`: removes unreferenced background functions | R9-5 |
| Rule titles: must be unique within a Feature (parse error on duplicate) | R9-6 |

### Assessment

After 9 rounds and 70+ issues found and resolved, the spec is in strong shape.
The remaining issues were one editing oversight (R9-1), one unreconciled
contradiction (R9-2), two gaps in file-management behavior (R9-3, R9-4), and
two minor edge cases (R9-5, R9-6). The core logic — vocabulary enforcement,
cache lifecycle, decorator resolution, strategy inference, Hypothesis binding —
holds up under adversarial walk-through.
