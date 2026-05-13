# beehave v2 Spec Post-Mortem — Round 8 (Adversarial Walk-Through)

> Mental adversarial walk-through of the complete v2 spec focusing on CLI
> commands, their inputs/outputs, and end-to-end user journeys. No code
> emulation — pure analysis of spec coherence and usability.
> Reviewed by System Architect (SA subagent).

---

## PP-V2-R8-H1: `sync` command referenced but never defined ✅ RESOLVED

**Severity:** High
**Location:** Cache File (line 373), Rebuild triggers (line 446)

The spec referenced `sync` in the cache lifecycle paragraph ("built on `sync`/`generate`") and the rebuild triggers table. But the CLI commands table only defined `generate`, `fix`, `clean`. In v1, `sync` assigned `@id` tags — v2 eliminated `@id` tags, making `sync` purposeless. Vestigial terminology.

**Resolution:** Removed all `sync` references. Cache lifecycle now says "built on `generate`." Rebuild triggers table uses just `generate`. No `sync` command exists in v2.

**Spec change applied:** Two edits — cache paragraph and rebuild triggers table.

---

## PP-V2-R8-H2: `name` parameter never defined ✅ RESOLVED

**Severity:** High
**Location:** CLI Commands (line 480-486)

All three CLI commands take `name` but the spec never defined what it is — feature file stem? path? glob? scenario title? Users had no way to know what to type.

**Resolution:** Defined `name` as a slash-separated path relative to `features_dir` (without `.feature` extension). Examples: `shopping` → `docs/features/shopping.feature`; `be/shopping` → `docs/features/be/shopping.feature`. Output mirrors the structure under `tests_dir`. Supports subfolders natively.

**Spec change applied:** Added `name` parameter definition block after the CLI commands table.

---

## PP-V2-R8-H3: Generated stub example shows implementation, not stub ✅ RESOLVED

**Severity:** High
**Location:** generate command (line 497-518), Body Enforcement (line 329-345)

The generated stub example showed a complete implementation (`remaining = initial - amount; assert remaining >= 0`) instead of what `generate` actually produces. This is misleading — `generate` cannot know the implementation. Additionally, if stubs use `pass` or `...`, body enforcement would immediately flag all placeholders as unreferenced, creating a chicken-and-egg problem: users can't collect the test until they write the body.

**Resolution:** Two-part fix:

1. **Generated stubs use `...` (Ellipsis) as the body** — honest stubs with no fake logic.
2. **Body enforcement has an Ellipsis exemption** — functions whose body is only `...` (single AST `Expr(Constant(value=Ellipsis))` node) are exempt from enforcement. Once the user replaces `...` with real code, enforcement activates.

**Spec change applied:** Replaced stub example body with `...`. Added "Stub exemption" paragraph to Body Enforcement section. Added clarifying note after generated stub example.

---

## PP-V2-R8-M4: Plain scenario Hypothesis case count unaddressed ✅ RESOLVED

**Severity:** Medium
**Location:** Hypothesis Binding (line 105-110), Configuration (line 320-325)

`outline_random_examples` only controlled Scenario Outline random cases. Plain scenarios with `<placeholders>` always got Hypothesis's default 100 cases with no config to control this — inconsistent and surprising.

**Resolution:** Renamed `outline_random_examples` to `max_examples`. Applies to **all** scenarios with `<placeholders>`. For Scenario Outline, `@Example` rows always run and `max_examples` adds N random cases beyond them. For plain scenarios, N random cases total. Default: 1 (same as previous `outline_random_examples` default). Controls `hypothesis.settings(max_examples)`.

**Spec change applied:** Updated Hypothesis Binding bullet, Configuration section (toml example, config table), and description text. Three separate edits.

---

## PP-V2-R8-M5: Background stub placement and naming undefined ✅ RESOLVED

**Severity:** Medium
**Location:** generate command, File Conventions

The spec showed background functions in test files but never defined where `generate` puts them, what they're named, or how shared backgrounds work across scenarios.

**Resolution:** `generate` emits background functions before test functions in the same file. Naming: `background_<name>` where `<name>` derives from feature title (feature-level background) or rule title (rule-level background), using the same underscore conversion as test function names. All scenarios in the feature that share a background reference the same function.

**Spec change applied:** Added "Background stubs" paragraph after the stub exemption note in the generate section.

---

## PP-V2-R8-L7: Cache paths — relative to what? ✅ RESOLVED

**Severity:** Low
**Location:** Cache File (line 373-374)

Cache example showed `"docs/features/shopping.feature"` but didn't specify relative to what (project root? CWD?).

**Resolution:** All paths in the cache and in `features_dir`/`tests_dir` config are relative to the project root (the directory containing `pyproject.toml`).

**Spec change applied:** Added sentence to Cache File section.

---

## PP-V2-R8-L6: "collection-time" is pytest-specific terminology ✅ RESOLVED

**Severity:** Low
**Location:** Body Enforcement (line 329), Collection-Time Check (line 455)

Spec claimed "runner-agnostic" but used "collection-time" (pytest concept) repeatedly. For other runners, this would be "import time."

**Resolution:** Added parenthetical at first use in both Body Enforcement and Collection-Time Check sections: "(i.e., at test discovery/setup time, before test execution)." Frames the concept as universal rather than pytest-specific.

**Spec change applied:** Two parenthetical additions.

---

## Summary

| Status | Count | IDs |
|--------|-------|-----|
| ✅ Resolved | 7 | R8-H1, R8-H2, R8-H3, R8-M4, R8-M5, R8-L7, R8-L6 |
| ⬇️ Dropped | 0 | |
| ❌ Pending | 0 | |
| **Total** | **7** | |

### Spec Changes

| Change | Source |
|--------|--------|
| Removed all `sync` command references | R8-H1 |
| Defined `name` parameter: slash-separated path relative to `features_dir` | R8-H2 |
| Generated stub body changed to `...`; Ellipsis exemption in body enforcement | R8-H3 |
| Renamed `outline_random_examples` → `max_examples`, broadened to all scenarios with placeholders | R8-M4 |
| Background stub placement: before test functions, named `background_<name>()` | R8-M5 |
| Cache and config paths relative to project root (pyproject.toml directory) | R8-L7 |
| "collection-time" clarified as "test discovery/setup time, before execution" | R8-L6 |
