# Post-Mortem: PP12 — And/But decorators not imported in generated stubs

**Date:** 2026-05-11
**Severity:** Critical
**MoSCoW:** Must
**Source:** Self-check dogfood exercise

## What Happened

When `beehave generate` creates a test stub from a .feature file containing `And` or `But` steps, it writes `@And(...)` and `@But(...)` decorators but only imports `Given, When, Then, Example` from `beehave.decorators`. The generated file is a `NameError` at import time — it cannot be loaded by pytest.

## Steps to Reproduce

1. Create a .feature file with `And` or `But` steps
2. Run `beehave sync` then `beehave generate`
3. Try to import the generated file

## Root Cause

`_generate_stub_content()` in `cli.py` maps step keywords to decorator names but does not include `And` and `But` in the import statement. The keyword mapping produces `@And` and `@But` decorators correctly, but the fixed import block at the top of the file omits them.

**Location:** `beehave/cli.py` — the import line template in `_generate_stub_content()`.

## Expected Behavior

Generated stubs should import `And` and `But` alongside `Given, When, Then, Example`, or should normalize `And`/`But` to the preceding step type (Given/When/Then) per Gherkin semantics.

## Actual Behavior

```python
from beehave.decorators import Given, When, Then, Example
# ... later:
@And('the drone population is 50')  # NameError: And is not defined
```

## Impact

- Any .feature file using `And` or `But` steps produces a test file that cannot be imported
- pytest collection fails entirely for the generated module
- Developer cannot run any tests from that feature

## Proposed Fix

Add `And, But` to the import line in `_generate_stub_content()`, or normalize to preceding step type.
