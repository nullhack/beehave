# Discovery: gen-tests-orphan-fix

## State
Status: IDENTIFIED

## Problem
`uv run task gen-tests --orphans` reports 4 false-positive orphan warnings.
The affected tests are in `tests/features/stub_sync/` and contain fixture strings
like `@id:aabbccdd` embedded in test data (not as real @id tags). The `gen-tests`
tool incorrectly parses these fixture strings as @id references, then finds no
matching Example in any .feature file, and flags the test as an orphan.

This is a pre-existing defect introduced when the `stub-sync` feature was shipped.
It was NOT introduced by `auto-id-generation`.

## Impact
- False-positive noise in `gen-tests --orphans` output
- Developers may ignore real orphan warnings because of the noise

## Proposed Fix
The `gen-tests` tool should only scan for `@id:` tags in test function *names*
(i.e., `def test_<feature>_<hex>()`) rather than scanning the full file content
for `@id:` patterns. This would eliminate false positives from fixture strings.

## Entities
| Type | Name | Candidate Class/Method | In Scope |
|------|------|----------------------|----------|
| Noun | orphan test | test with no matching @id in any .feature | Yes |
| Noun | fixture string | @id-like text inside test body (not a real tag) | Yes |
| Verb | detect orphan | identify tests with no matching @id | Yes |
| Verb | false positive | incorrectly flagging a non-orphan as orphan | Yes |

## Questions
| ID | Question | Answer | Status |
|----|----------|--------|--------|
| Q1 | Should the fix scan function names only, or use a smarter heuristic? | TBD — needs stakeholder input | OPEN |
