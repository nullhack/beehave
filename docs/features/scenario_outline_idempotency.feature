Feature: Scenario Outline Idempotency

  Re-running beehave generate on a .feature file with Scenario Outline + Examples must not append duplicate test functions. Currently, expanded rows receive random @ids on each parse, so the deduplication check fails and duplicates are appended. This violates the product definition's idempotency quality attribute. This feature addresses PP13.

  Rules (Business):
  - When parse_feature() expands Scenario Outline Examples rows, each row's @id must be deterministic — derived from the scenario heading's @id and the row index
  - When generate() is run twice on the same .feature file, no duplicate test functions are created
  - Reordering Examples rows changes @ids (acceptable — row reordering is a semantic change)

  Constraints:
  - .feature files are the source of truth — beehave never modifies step text in .feature files
  - Idempotency for Scenario Outline (QA13): when generate() is run twice on the same .feature file, no duplicate test functions are created
  - Same @ids produced for same expanded rows across parses
  - Architecture decision AD4: derive expanded-row @ids from hash(scenario_heading_id + str(row_index)) truncated to 8 hex characters
  - MoSCoW: Must

  ## Changes

  | Session | Change |
  |---------|--------|
  | 2026-05-11 | Created: PP13 — Deterministic @id generation for Scenario Outline expanded rows |

  Rule: Expanded row @ids are deterministic across parses
    As a property-based TDD developer
    I want expanded-row @ids to be the same on every parse of the same .feature file
    So that re-running generate does not create duplicate test functions

    @id:d70b43c7
    Example: Same Examples rows produce same @ids across two parses
      Given a .feature file with "Scenario Outline: parameterized" and 3 Examples rows
      When parse_feature() is called twice
      Then the @ids of all expanded rows are identical between both parses

    @id:6bf99005
    Example: Different row indices produce different @ids
      Given a .feature file with "Scenario Outline: test" and 2 Examples rows
      When parse_feature() expands the rows
      Then row 0 and row 1 have different @id tags

  Rule: Generate is idempotent for Scenario Outline
    As a QA engineer
    I want beehave generate to be idempotent — running it twice produces no new test functions
    So that the workflow is safe and predictable

    @id:af9221cf
    Example: Running generate twice appends no duplicates
      Given a .feature file with "Scenario Outline: values" and 2 Examples rows
      And beehave generate has been run once, producing 2 test functions
      When beehave generate is run a second time
      Then no new test functions are appended
      And the test file still contains exactly 2 test functions

    @id:146758c7
    Example: Running generate multiple times is idempotent
      Given a .feature file with Scenario Outline and Examples
      When beehave generate is run 3 times consecutively
      Then the test file contains exactly one test function per Examples row
