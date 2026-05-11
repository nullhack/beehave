# PM_20260511_generate_silent_skip_no_id: generate() silently skips scenarios without @id tags

## Failed At

CLI `generate()` — self-validation tester: after writing 3 `Scenario:` blocks without `@id` tags and running `generate()`, the output says "no scenarios found" despite 3 scenarios clearly existing in the file. No guidance is given about needing to run `sync()` first.

## Root Cause

`generate()` in `cli.py:46` filters scenarios to only those with `id_tag is not None`: `orphans = [s for s in scenarios if s.id_tag is not None]`. If no scenarios have `@id` tags, the `orphans` list is empty, and the result is `{action: "skipped", reason: "no scenarios found"}`. The message "no scenarios found" is misleading — scenarios were found, they just don't have `@id` tags.

The developer experience is: write `.feature` → run `generate()` → "no scenarios found" → confusion. The correct workflow is: write `.feature` → run `sync()` → run `generate()`. But `generate()` doesn't hint at this.

## Missed Gate

The generate tests (traceability_generate_core, traceability_generate_modes) always start from `.feature` files that already have `@id` tags (because sync was run during test setup). No test exercises `generate()` on a `.feature` file without `@id` tags.

## Fix

1. Change the "no scenarios found" message to distinguish between "file has no scenarios at all" and "file has N scenarios but none have @id tags — run `beehave sync` first".
2. Better: have `generate()` auto-detect scenarios without `@id` tags and either run `sync()` automatically or return a clear actionable message like "3 scenarios found without @id tags. Run `beehave sync` to assign IDs, then re-run generate."
3. Add a test for `generate()` on a feature file with scenarios but no `@id` tags.

## Restart Check

Create a `.feature` with scenarios but no `@id:` tags. Run `generate()`. Verify output says "N scenarios found without @id tags" or similar, not "no scenarios found".
