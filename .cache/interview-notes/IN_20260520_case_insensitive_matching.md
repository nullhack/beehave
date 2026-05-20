# Interview Notes: Case-Insensitive Matching

**Session:** IN_20260520_case_insensitive_matching
**Date:** 2026-05-20
**Stakeholder:** Product Owner (adversarial code review)

---

## Pain Points

| # | Description | Severity | Location |
|---|-------------|----------|----------|
| 18 | Negative numbers invisible — `_extract_body_nodes` misses `UnaryOp(USub(), Constant(n))` | High | `discover.py:44-48` |
| 19 | Quoted placeholder double-capture — `"<name>"` extracted as both Placeholder and Literal | Medium | `gherkin.py:88-96` |
| 20 | Quoted bracket notation captured as literal — `"[PHONE]"` becomes Literal when intent is markup | Medium | `gherkin.py:88-96` |
| 22 | Type mismatch — Gherkin `int(77000)` vs AST `str("77000")` from `Decimal("77000")` | High | `check.py:55` |

## Business Goals

1. **Case-insensitive matching for placeholders and literals.** `<Dog>` in Gherkin must match `dog`, `DOG`, `Dog` in test body. `"Rex"` in Gherkin must match `"rex"`, `"Rex"`, `"REX"` in test body.

## Formal Rules

### R1 — Placeholder Extraction
A `<token>` in step text is a Placeholder iff `token` is a valid Python identifier, not a Python keyword, not a Python builtin. Placeholder regex matches regardless of surrounding quotes. Duplicate placeholders within a step are deduplicated.

### R2 — Numeric Literal Extraction
A bare token in step text is a numeric Literal iff it matches `^-?\d+$`.

### R3 — String Literal Extraction
A quoted segment (`"..."` or `'...'`) is a string Literal with content extracted as-is between quotes. Exception: `<...>` inside quotes is skipped (already captured as Placeholder via R1). `[...]` inside quotes is captured verbatim as a literal value.

### R4 — AST Body Constant Extraction
`_extract_body_nodes` collects: (a) `ast.Constant` values directly, (b) folded `UnaryOp(USub(), Constant(n))` → `-n`. Leading docstring expression is excluded.

### R5 — Placeholder Comparison (case-insensitive)
A placeholder `ph` matches iff `ph.name.lower()` is in `{n.lower() for n in ti.body_name_nodes}`.

### R6 — Literal Comparison (string-normalized, case-insensitive)
A literal `lit` matches iff `str(lit.value).lower()` is in `{str(c).lower() for c in ti.body_constant_nodes}`.

## Domain Terms

| Term | Definition |
|------|-----------|
| Placeholder | `<name>` in Gherkin step text, mapped to Hypothesis strategy parameter |
| Literal | Numeric token or quoted string in Gherkin step text, must appear in test body |
| body_name_nodes | All `ast.Name` identifiers in test function body (after docstring exclusion) |
| body_constant_nodes | All `ast.Constant` values in test function body (after docstring exclusion, plus folded UnaryOp) |
| Case-insensitive matching | Comparison normalizes both sides to lowercase string form |

## Edge Cases

| Case | Expected |
|------|----------|
| `-2010` in Gherkin, `x = -2010` in body | Match (#18 fix) |
| `-3.14` in Gherkin, `x = -3.14` in body | Match |
| `"<phone>"` in Gherkin step with `Scenario Outline` | Placeholder extracted, literal skipped (#19 fix) |
| `"[PHONE]"` in Gherkin, body has `"555-1234"` | `[PHONE]` is a literal matching literal `[PHONE]`; user writes different value → missing-literal (correct — user should use placeholders for dynamic values) |
| `"Rex"` in Gherkin, `"rex"` in body | Match (case-insensitive) |
| `<Dog>` in Gherkin, `Dog` class in body | Match (case-insensitive) |
| `77000` in Gherkin, `Decimal("77000")` in body | Match (#22 fix via string normalization) |
| `1` in Gherkin, `True` in body | No match — `"1" != "true"` |
| Leading docstring in test body | Excluded from constant collection (existing behavior, unchanged) |
| Stub test bodies | Skipped entirely (existing behavior, unchanged) |

## Files Affected

| File | Change |
|------|--------|
| `beehave/discover.py` | `_extract_body_nodes`: fold UnaryOp (#18) |
| `beehave/gherkin.py` | `_extract_literals`: filter `<...>` from quoted captures (#19, #20) |
| `beehave/check.py` | `_check_placeholders`: case-insensitive (R5); `_check_literals`: string-normalized case-insensitive (R6, fixes #22, hardens #18) |
| `tests/` | New edge case tests for all 4 bugs + case variations |

## Scope

Single feature. Changes localized to extraction and comparison functions within Feature Parsing, Consistency Checking, and Test Discovery bounded contexts. No new bounded contexts, no cross-cutting concerns, no new dependencies.

## Quality Attributes

- **Correctness:** Deterministic comparison — same inputs always yield same result
- **Reliability:** No false positives (existing test suite guards against regression)
- **Simplicity:** string-based comparison replaces type-based + multiple special cases
