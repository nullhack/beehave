Feature: Fix Command Alignment

  The beehave fix command must use content-based diff alignment (not positional comparison) to accurately match .feature steps to existing test decorators. When a developer inserts a new step mid-scenario, fix must propose a single insertion — not a cascade of N text replacements. This replaces the positional comparison in _find_text_mismatches() with difflib.SequenceMatcher.

  Rules (Business):
  - When a step is inserted mid-scenario in a .feature file, fix must propose a single insertion rather than N text replacements for every subsequent step
  - When a step is deleted from a .feature file, fix must propose a single deletion rather than N text replacements
  - When _find_text_mismatches() compares feature steps to test decorators, it must use difflib.SequenceMatcher with autojunk=False for content-based alignment
  - A Mismatch must carry the expected text and actual text for reporting, classified as equal, replace, insert, or delete via get_opcodes()
  - The developer can see the actual number and type of changes needed when running fix --dry-run, enabling informed decision-making
  - FixMismatch can propose accurate changes when using diff-based alignment, even for mid-sequence insertions and deletions
  - Fix must handle the case where step text changed (not just shifted) — content-based matching must not falsely align different text

  Constraints:
  - Fix accuracy (QA10): when a step is inserted mid-scenario, fix proposes a single insertion; fix --dry-run shows 1 insertion, not N replacements
  - Idempotency: running fix multiple times produces the same result — once changes are applied, a subsequent fix reports no mismatches
  - Safety: fix --dry-run shows changes without modifying files; fix without --dry-run modifies files after confirmation
  - Architecture decision AD2: use difflib.SequenceMatcher (stdlib) with autojunk=False; get_opcodes() classifies equal/replace/insert/delete
  - SequenceMatcher is O(n²) worst case but typical step counts are under 20 — performance is negligible
  - MoSCoW: Should

  ## Changes

  | Session | Change |
  |---------|--------|
  | 2026-05-11 | Created: PP10 — fix step insertion misalignment from positional comparison |
