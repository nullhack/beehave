# PM_20260511_unescaped_quotes_in_stubs: Generated decorator strings contain unescaped quotes

## Failed At

CLI `generate()` — self-validation tester: generated file `tests/features/hive_inspection/default_test.py` has `@Given("hive "Alpha" has 10 frames of bees")` on line 11 — nested double quotes produce `SyntaxError: invalid syntax`. The file cannot be imported by pytest.

## Root Cause

`_generate_stub_content()` in `cli.py:270-271` writes step decorators as `f'@{keyword}("{step_text}")'` without escaping any characters in `step_text`. When the Gherkin step text contains double quotes (e.g., `hive "Alpha"`), the generated Python string literal breaks because the inner quotes are not escaped. The generator should either use single quotes for the outer string when the step text contains double quotes, or escape the inner quotes.

## Missed Gate

All existing feature files (traceability_generate_core, traceability_generate_modes, step_decorators_strategy_resolution) use step text without embedded quotes. No test exercises a `.feature` file with quoted values in step text. The generator was only validated against the simplest possible Gherkin patterns.

## Fix

1. In `_generate_stub_content()`, detect if `step_text` contains the chosen quote character and switch to the alternate quote, or use escaped quotes (`\"`).
2. Safer approach: always use single quotes for the outer decorator string and escape any single quotes in the step text. Or use a raw string or triple-quoted string.
3. Add a test that generates stubs from a feature with quoted values in step text and verifies the generated file compiles as valid Python.

## Restart Check

Create a `.feature` with step text `Given hive "Alpha" has 10 frames`, run `generate()`, verify the output file passes `py_compile.compile()` and `pytest --collect-only`.
