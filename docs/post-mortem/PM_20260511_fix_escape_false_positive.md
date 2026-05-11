# Post-Mortem: PP14 — Fix command false positive on escape sequences

**Date:** 2026-05-11
**Severity:** Medium
**MoSCoW:** Should
**Source:** Self-check dogfood exercise

## What Happened

The `beehave fix` command reports a text mismatch between the decorator `@And('the hive\\'s honey stores are replenished')` in the test file and the step text `the hive's honey stores are replenished` in the .feature file. The `\\'` is the Python source representation of an escaped single quote — semantically identical to `'s`. Fix reports this as a mismatch and applying the "fix" does not resolve it, creating an infinite loop.

## Steps to Reproduce

1. Create a .feature file with a step containing an apostrophe (e.g., `the hive's honey stores`)
2. Run `beehave sync` then `beehave generate` — produces `@And('the hive\'s honey stores are replenished')`
3. Run `beehave fix --dry-run` — reports mismatch between `\\'` in test and `'` in feature
4. Run `beehave fix` — applies change but the escape persists
5. Run `beehave fix --dry-run` again — still reports the same mismatch

## Root Cause

`_align_steps()` compares decorator text extracted by `_DECORATOR_RE` regex against step text from the .feature file. The decorator text includes the Python escape (`\'`) while the .feature text has the raw character (`'`). The comparison is literal string equality — it does not account for Python string escaping.

**Location:** `beehave/cli.py:_align_steps()` — compares raw decorator text to raw feature step text.

## Expected Behavior

`beehave fix` should not report a mismatch when the only difference is Python string escaping of quote characters.

## Actual Behavior

```
-@And('the hive\\'s honey stores are replenished')
+@And('the hive\'s honey stores are replenished')
```

This diff is a false positive — both lines represent the same Python string.

## Impact

- Fix command reports phantom mismatches for any step text containing apostrophes
- Developers lose trust in fix output (wolf-crying)
- Cannot distinguish real mismatches from escape false positives

## Proposed Fix

When comparing decorator text to feature step text, unescape Python string escapes in the decorator text before comparison. Use `bytes(text, 'utf-8').decode('unicode_escape')` or a targeted `replace("\\'", "'")` / `replace('\\"', '"')`.
