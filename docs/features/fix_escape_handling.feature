Feature: Fix Escape Handling

  The fix command must compare decorator text to feature step text semantically, not literally. Currently, escaped quotes in Python string literals (e.g., `\'` in `@And('the hive\'s honey stores')`) are compared literally against the .feature file's `the hive's honey stores`, producing a false mismatch. Applying the "fix" doesn't resolve it, creating an infinite loop. This feature addresses PP14.

  Rules (Business):
  - When fix() compares decorator text to feature step text, semantically identical strings must match regardless of Python escape sequences
  - When the only difference is Python string escaping (e.g., `\'` vs `'`), no mismatch is reported
  - When a genuine text difference exists (not just escaping), the mismatch is reported normally

  Constraints:
  - .feature files are the source of truth — beehave never modifies step text in .feature files
  - Escape-aware comparison (QA14): when fix() compares decorator text to feature step text, semantically identical strings match
  - No false mismatch on escaped quotes; fix loop is broken
  - MoSCoW: Should

  ## Changes

  | Session | Change |
  |---------|--------|
  | 2026-05-11 | Created: PP14 — Escape-aware comparison in fix command |

  Rule: Escaped quotes in decorator text match unescaped quotes in feature step text
    As a property-based TDD developer
    I want fix() to treat `\'` in decorator text as semantically identical to `'` in feature step text
    So that escape sequences do not produce false mismatches

    @id:d4e5f6a7
    Example: Single-quoted escape matches unescaped apostrophe
      Given a decorator with text "the hive's honey stores" and a feature step "the hive's honey stores"
      When fix() compares the texts
      Then no mismatch is reported

    @id:b8c9d0e1
    Example: Double-quoted escape matches unescaped double quote
      Given a decorator with text 'hive "Alpha" has 10 frames' and a feature step 'hive "Alpha" has 10 frames'
      When fix() compares the texts
      Then no mismatch is reported

  Rule: Genuine text differences are still detected
    As a QA engineer
    I want fix() to report actual text mismatches that are not just escape differences
    So that real step text changes are caught

    @id:f2a3b4c5
    Example: Different step text is reported as mismatch
      Given a decorator with text "the hive has 10 frames" and a feature step "the hive has 20 frames"
      When fix() compares the texts
      Then a mismatch is reported

    @id:6d7e8f9a
    Example: Escaped text that differs in content is reported as mismatch
      Given a decorator with text "the hive's honey" and a feature step "the hive's nectar"
      When fix() compares the texts
      Then a mismatch is reported (content differs, not just escaping)
