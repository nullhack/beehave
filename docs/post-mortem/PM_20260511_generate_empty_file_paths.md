# PM_20260511_generate_empty_file_paths: Generated stub output shows empty file paths

## Failed At

CLI `generate()` command — dogfood user: "Created  for @a1b2c3d4" output shows empty string where file path should be.

## Root Cause

`_process_scenario()` in `cli.py` returns a dict with `test_file` key, but `_format_text_output()` reads from `r.get('test_file', '')` while the returned dict uses `r.get('file', '')` (the key is `file`, not `test_file`). The format function references a key that doesn't exist in the result dict, producing empty strings.

## Missed Gate

Traceability test for feature 2b (traceability_generate_core) validated that stubs are created and contain correct content, but did not verify the human-readable output string returned by `generate()`. The test only checked the return value for JSON mode, not text mode.

## Fix

Align the keys: either `_process_scenario` should return `test_file` instead of `file`, or `_format_text_output` should read `r.get('file', '')` instead of `r.get('test_file', '')`. Add a test that calls `generate()` in text mode and asserts the output contains the expected file path.

## Restart Check

Run `generate('decorator_test')` in text mode and verify output contains `tests/features/decorator_test/default_test.py` — not an empty string after "Created".
