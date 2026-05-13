# PM_20260511_fix_step_insertion_misalignment: Fix command misinterprets step insertion as text replacement cascade

## Failed At

CLI `fix()` — self-validation tester: after inserting a new step "And hive 'Lambda' was inspected within the last 7 days" into the middle of a scenario, `fix --dry-run` proposes replacing 4 existing decorator texts by shifting them all one position, instead of inserting the new decorator and keeping existing ones unchanged.

## Root Cause

`_find_text_mismatches()` in `cli.py:520-546` compares feature steps and test decorators position-by-position (index `i` in both lists). When a new step is inserted at position 2, all subsequent steps shift by one position. The diff algorithm sees: position 2 now has new text (vs old), position 3 has old position 2 text (vs old position 3), etc. It interprets this as every decorator needing text replacement rather than one insertion.

The fix command has no concept of diffing — it does simple positional alignment. It cannot distinguish "text changed at position N" from "text inserted at position N, shifting all subsequent".

## Missed Gate

Feature 2d (traceability_fix_clean) tests `fix()` for text replacement (step text changed) and missing decorator addition (new step at the end). No test exercises inserting a step in the middle of an existing scenario. The fix command was designed for the two simplest mutation types, not the general case.

## Fix

1. Use a proper diff algorithm (Longest Common Subsequence or similar) to match feature steps to existing decorators by content similarity, not just position.
2. If an existing decorator's text matches a later feature step, recognize it as an insertion rather than a modification.
3. At minimum, detect the pattern where `N` consecutive decorators match `N` feature steps at offset `+1` and treat it as a single insertion.
4. Add test for mid-scenario step insertion.

## Restart Check

Create a `.feature` with scenario steps A, B, C. Generate stubs. Insert step X between B and C in the `.feature`. Run `fix --dry-run`. Verify it proposes `+@And("X")` only, not replacements for B and C.
