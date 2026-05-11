# PM_20260511_step_leakage_across_scenarios: Steps leak across scenario boundaries when Scenario Outline follows

## Failed At

CLI `generate()` — self-validation tester: `@id:6399af56` ("Disease detected during inspection") receives 4 extra step decorators from the `Scenario Outline: Varroa mite count assessment` that follows it. The generated test function `test_disease_detected_during_inspection_6399af56` incorrectly has `@Given("hive "<hive_name>" has a Varroa mite count...")` and 3 more Varroa steps appended after its own steps.

## Root Cause

`_parse_feature_steps()` in `cli.py:323-342` collects steps for a given `@id` by scanning forward from the `@id:` tag line until it encounters a section break. The section break check in `_is_section_break()` at `traceability.py:156-157` only checks for `Example:`, `Scenario:`, `Rule:`, and `Feature:`. Since `Scenario Outline:` is not in `_SECTION_BREAK_KEYWORDS`, the parser never stops collecting steps for `@id:6399af56` — it continues through the `Scenario Outline:` heading and collects all its steps too.

## Missed Gate

No test exercises two consecutive scenarios where the second is a `Scenario Outline:`. The `_parse_feature_steps()` tests only verify steps within a single scenario, not boundary behavior between different scenario types.

## Fix

1. Add `"Scenario Outline:"` and `"Scenario Template:"` to `_SECTION_BREAK_KEYWORDS` in `traceability.py`.
2. Better: make the section break check prefix-based rather than exact-match — any line starting with `Scenario` or `Example` should be a section break.
3. Add a test where `Scenario Outline:` follows a `Scenario:` and verify steps don't leak.

## Restart Check

Create a `.feature` with `@id:xxx\nScenario: A\n  Given x\n  When y\nScenario Outline: B\n  Given <p>\nExamples:\n  | p |\n  | 1 |`, run `_parse_feature_steps()`, verify `@id:xxx` has exactly 2 steps (Given x, When y), not 3+.
