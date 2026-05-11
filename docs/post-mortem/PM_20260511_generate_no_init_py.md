# PM_20260511_generate_no_init_py: Generated test directory has no __init__.py

## Failed At

CLI `generate()` — dogfood user: `tests/features/decorator_test/` directory is created with `default_test.py` but no `__init__.py`. Python requires `__init__.py` for proper test collection in some configurations.

## Root Cause

`_ensure_test_directory()` calls `os.makedirs(feature_name, exist_ok=True)` but does not create an `__init__.py` file. The function only ensures the directory exists.

## Missed Gate

No test verified that `generate()` creates a complete, importable Python package. Tests checked that the test file is created with correct content but not that the directory is a proper package.

## Fix

`_ensure_test_directory()` should create `__init__.py` (empty file) after `os.makedirs()`:
```python
init_path = os.path.join(feature_name, "__init__.py")
if not os.path.exists(init_path):
    Path(init_path).touch()
```

## Restart Check

Generate stubs for a new feature. Verify `tests/features/<name>/__init__.py` exists alongside the test file.
