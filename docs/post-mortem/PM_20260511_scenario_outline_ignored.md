# PM_20260511_scenario_outline_ignored: Scenario Outline not recognized by parser

## Failed At

CLI `generate()` / `sync()` — self-validation tester: "Varroa mite count assessment" (a `Scenario Outline:` with 4 `Examples:` rows) is completely invisible to `parse_feature()` — no `@id` tag assigned, no stub generated, no warning emitted.

## Root Cause

`_is_scenario_heading()` in `traceability.py:148-149` only matches lines starting with `Example:` or `Scenario:` — it does not match `Scenario Outline:` (or its alias `Scenario Template:`). This is a Gherkin keyword defined in the official specification but missing from the parser's recognition list.

## Missed Gate

Feature 3a (feature_parsing_mapping) tests only `Scenario:` and `Example:` headings. No test exercises `Scenario Outline:`, `Scenario Template:`, or the `Examples:` block. The traceability parser test suite was designed against the minimal subset used in earlier features rather than the full Gherkin keyword reference.

## Fix

1. Extend `_is_scenario_heading()` to also match `Scenario Outline:` and `Scenario Template:` (the Gherkin-6 official aliases).
2. When a `Scenario Outline` is found, expand it into one `Scenario` per row in the `Examples:` table, substituting `<placeholder>` values. Each expanded row needs its own `@id`.
3. Add tests for `Scenario Outline:` and `Scenario Template:` parsing.

## Restart Check

Create a `.feature` file with `Scenario Outline:` + `Examples:` table, run `sync()`, verify each example row gets its own `@id` and `parse_feature()` returns one `Scenario` per row.
