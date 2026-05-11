# Post-Mortem: PP13 — Scenario Outline expanded rows are not idempotent

**Date:** 2026-05-11
**Severity:** Critical
**MoSCoW:** Must
**Source:** Self-check dogfood exercise

## What Happened

Running `beehave generate` twice on a .feature file containing `Scenario Outline:` with `Examples:` tables appends duplicate test functions on the second run instead of skipping them. Each re-parse generates new random @ids for expanded rows, so the deduplication check (which looks for existing @ids in the test file) fails.

## Steps to Reproduce

1. Create a .feature file with a `Scenario Outline:` and `Examples:` table with 2 rows
2. Run `beehave sync` then `beehave generate` — creates 2 expanded test functions with random @ids
3. Run `beehave generate` again — appends 2 MORE test functions with different random @ids

## Root Cause

`parse_feature()` in `traceability.py` expands Scenario Outline Examples rows into separate `Scenario` entities, each with a freshly generated `IdTag` via `generate_id()`. Since the @ids are random, they differ on each parse. The `generate()` function's deduplication logic (checking if an @id already exists in the test file) correctly skips scenarios with stable @ids (regular `Scenario:` headings), but cannot match the expanded-row @ids because they change on every call.

**Location:** `beehave/traceability.py:_try_append_scenario()` — generates new `IdTag` for each expanded row instead of deriving a deterministic ID.

## Expected Behavior

Re-running `beehave generate` should be idempotent — no new test functions appended for existing scenarios.

## Actual Behavior

```
First run:  Created tests/features/self_check/default_test.py for @aaa11111 @bbb22222 @ccc33333 @ddd44444
Second run: Appended to tests/features/self_check/default_test.py: @eee55555 @fff66666 @ggg77777 @hhh88888
```

## Impact

- Scenario Outline expanded rows accumulate duplicates on every generate run
- Developers must manually clean up or delete and regenerate
- Idempotency quality attribute is violated for the most common Scenario Outline pattern

## Proposed Fix

Derive expanded-row @ids deterministically from the Scenario Outline heading's @id + row index or row content hash. This ensures the same rows always produce the same @ids across parses.
