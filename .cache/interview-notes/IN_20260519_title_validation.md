# Interview Notes: beehave Title Validation

**Session:** IN_20260519_title_validation
**Date:** 2026-05-19
**Stakeholder:** Project owner
**Domain status:** already-known (stakeholder provided full specification)

## Pain Points

- `beehave check` does not detect duplicate feature titles across `.feature` files
- `beehave check` does not detect duplicate rule titles within a feature
- `beehave check` does not detect duplicate scenario titles
- `beehave check` does not validate title word count
- `beehave generate` silently generates stubs even when `.feature` files have title issues — no pre-flight validation

## Business Goals

- All Gherkin titles (Feature, Rule, Scenario, Scenario Outline) must conform to charset and word count rules
- All titles must be unique case-insensitively across the entire project, across all three title types
- `beehave check` must surface title violations alongside existing checks
- `beehave generate` must refuse to generate stubs if any `.feature` file in the project has title violations

## Validation Rules

### Charset

`[\w\s]+` — word characters and spaces only. This rule already exists in `_validate_title()`.

### Word Count

2–6 words, counting only the title text — not the Gherkin keyword prefix (`Feature:`, `Rule:`, `Scenario:`, `Scenario Outline:`).

### Uniqueness

Case-insensitive comparison across the entire project. All three title types (Feature, Rule, Scenario) share the same global namespace — a Feature title must not match any Rule or Scenario title, and vice versa.

## New Violation Types

Six new violation types added to the Violation entity:

| error_type | Trigger |
|-----------|---------|
| `invalid-feature-title` | Feature title fails charset or word count |
| `invalid-rule-title` | Rule title fails charset or word count |
| `invalid-scenario-title` | Scenario/Scenario Outline title fails charset or word count |
| `duplicate-feature-title` | Feature title matches another Feature title (case-insensitive) |
| `duplicate-rule-title` | Rule title matches another Rule or any Feature/Scenario title (case-insensitive) |
| `duplicate-scenario-title` | Scenario title matches another Scenario or any Feature/Rule title (case-insensitive) |

## Commands Affected

### beehave check

`check_all()` calls `validate_all_titles(config)` alongside existing checks. Title violations are returned in the same `list[Violation]` and reported to the user.

### beehave generate

Pre-flight: before calling `parse_feature()` for the target feature, `beehave generate` runs `validate_all_titles(config)` across **all** `.feature` files. If any violations are found, generation is refused and the command exits with code 1. No stubs are written.

## Files Changed

| File | Change |
|------|--------|
| `beehave/gherkin.py` | Extend `_validate_title()` with word count (2–6 words, prefix-stripped). Add new function `validate_all_titles(config) → list[Violation]` that scans all `.feature` files and checks charset, word count, and global uniqueness. |
| `beehave/check.py` | `check_all()` calls `validate_all_titles()` and appends results to the violation list. |
| `beehave/generate.py` | Pre-flight call to `validate_all_titles()` before `parse_feature()`. Exit 1 if violations found. |

## Edge Cases

- Empty title (0 words) → invalid (falls below 2-word minimum)
- Single-word title → invalid (below 2-word minimum)
- Titles exceeding 6 words → invalid
- Titles with special characters outside `[\w\s]` → invalid (existing behavior)
- Case-insensitive duplicates: "Hive Activity" and "hive activity" collide
- Cross-type duplicates: Feature "Login" and Scenario "Login" collide
- Multiple `.feature` files with same Feature title → duplicate
- Singleton `.feature` file with unique valid titles → zero title violations
- Title text extracted correctly: `Feature: Hive Activity` → word count on `Hive Activity` only (2 words)

## Scope Decisions

- **No backward compatibility flag.** Title validation is strict — no `--lenient` or `--skip-title-check` flag.
- **All-or-nothing for generate.** Pre-flight scans all `.feature` files, not just the target feature. One bad title anywhere blocks all generation.

## Domain Terms

- **Feature title:** The text following `Feature:` on the first non-comment line of a `.feature` file
- **Rule title:** The text following `Rule:` within a feature
- **Scenario title:** The text following `Scenario:` or `Scenario Outline:` within a feature
- **Title text:** The title string with the Gherkin keyword prefix stripped
- **validate_all_titles():** New function in `beehave/gherkin.py` that scans all `.feature` files and returns `list[Violation]`

## Quality Attributes

| Attribute | Relevance |
|-----------|-----------|
| Correctness (Must) | Duplicate/invalid titles cause downstream function-name collisions; validation prevents non-deterministic behavior |
| Reliability (Must) | `generate` refusing with exit 1 on title violations maintains "zero partial output on failure" |
| Simplicity (Must) | Title validation is an internal beehave concern — no new imports in generated code |

## Notes

- Feature name: `title_validation`
- The Violation entity (`domain_spec.md:119-128`) already supports extension via the `error_type` field — no schema change required
- `_validate_title()` already exists in `beehave/gherkin.py` with charset-only validation; this feature extends it with word count
- Title validation belongs primarily to the Feature Parsing context, with downstream integration into Consistency Checking and Code Generation
