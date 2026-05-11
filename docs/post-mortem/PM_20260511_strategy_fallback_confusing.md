# PM_20260511_strategy_fallback_confusing: Strategy fallback to st.integers() produces surprising values

## Failed At

Decorator strategy resolution — dogfood user: a test with `<parts>` placeholder where no `parts_strategy` variable exists silently falls back to `st.integers()`, which generates 0, negative numbers, and any integer. This produces `ZeroDivisionError` and confusing assertion failures that don't match the test's intent.

## Root Cause

`_resolve_placeholder()` in `decorators.py` falls back to `st.integers()` when no module-level strategy and no @Example type inference is available. The fallback is a reasonable default for generic cases but dangerous for domain-specific constraints (e.g., "parts must be ≥ 1"). There is no warning or logging that the fallback was used.

## Missed Gate

The `step_decorators_strategy_resolution` feature tested the fallback behavior (feature spec: "Strategy resolution priority: module-level variable → @Example type inference → st.integers() fallback") but did not evaluate the developer experience of silent fallback. The spec treats fallback as correct behavior rather than a potential footgun.

## Fix

Three options (not mutually exclusive):
1. **Warn on fallback**: When `st.integers()` is used as fallback, emit a `warnings.warn()` so developers know which placeholders lack strategies.
2. **Smarter fallback**: Use `st.from_type()` based on the @Example value if one exists, instead of always `st.integers()`. The code already has this logic but it produces `st.from_type(type(examples[name]))` which for `int` → `st.integers()`.
3. **Document convention**: The getting-started guide should emphasize defining a `<name>_strategy` variable for every placeholder.

Option 1 is the minimum viable fix — it makes the invisible visible.

## Restart Check

Write a test using `@Given("a hive with <parts> equal jars")` with no `parts_strategy` defined. Run with warnings enabled. A `UserWarning` should appear mentioning `parts` fell back to `st.integers()`.
