# PM_20260511_generate_stub_no_skip_marker: Generated stubs have no @pytest.mark.skip

## Failed At

CLI `generate()` — dogfood user: generated stubs use `...` (Ellipsis) as the function body with no `@pytest.mark.skip` decorator. When collected by pytest, these stubs execute silently (Ellipsis is a valid expression) and pass, giving false confidence that unimplemented behavior is tested.

## Root Cause

`_generate_stub_content()` produces `def test_foo(): ...` with no skip marker. The design intent was likely that `...` would cause a failure, but in Python, Ellipsis is a valid no-op expression. A test with `...` body passes immediately.

This conflicts with the project's own TDD convention where stubs use `@pytest.mark.skip(reason="not yet implemented")` and `raise NotImplementedError`.

## Missed Gate

The `traceability_generate_core` feature validated stub creation and ID extraction but did not enforce that stubs are skipped or fail by default. The feature spec describes stubs as "skeletons" but never specifies their execution behavior.

## Fix

Update `_generate_stub_content()` to include:
```python
import pytest

@pytest.mark.skip(reason="not yet implemented")
def test_foo():
    raise NotImplementedError
```

## Restart Check

Generate stubs for a new feature. Run `pytest` on the generated file. All generated tests should appear as SKIPPED, not PASSED.
