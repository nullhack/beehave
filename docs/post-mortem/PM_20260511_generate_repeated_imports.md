# PM_20260511_generate_repeated_imports: Generated stubs repeat import block per scenario

## Failed At

CLI `generate()` — self-validation tester: appending a second/third scenario to `default_test.py` repeats the entire import block (`from beehave.decorators import ...`, `from hypothesis import strategies as st`, `# Strategy variables`, `default_strategy = st.integers()`) for each scenario.

## Root Cause

`_generate_stub_content()` produces a self-contained Python file with imports and strategy boilerplate. When `_process_scenario()` detects the file exists, it calls `_append_function_stub()` which concatenates the full stub content to the existing file. There is no logic to detect that imports are already present and strip them from appended content.

## Missed Gate

The `traceability_generate_core` feature tests verified that appending works (file exists → append mode), but the test assertions only checked that the function name and ID appear in the file — they did not inspect the file for duplicated imports or structural quality.

## Fix

Two options:
1. **Simple**: `_generate_stub_content()` should accept a flag `is_append=False` that omits imports when appending.
2. **Better**: `_append_function_stub()` should strip leading import/comment lines from `content` when the target file already contains them.

Add a test that generates two scenarios into the same file and asserts the import block appears exactly once.

## Restart Check

Generate stubs for a feature with 3+ scenarios. The output file should have one import block at the top, followed by all test functions.
