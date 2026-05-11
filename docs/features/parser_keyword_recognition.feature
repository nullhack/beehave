Feature: Parser Keyword Recognition

  The Gherkin parser must recognize all Gherkin-6 scenario heading keywords (Scenario Outline:, Scenario Template:) and enforce step boundary integrity so that steps never leak across scenario boundaries. This feature addresses PP7 (scenario outlines invisible to the parser) and PP9 (steps leak into adjacent scenarios), which share a root cause: missing keyword recognition in _is_scenario_heading() and missing section-break reset logic in _parse_feature_steps().

  Rules (Business):
  - When a .feature file containing Scenario Outline: or Scenario Template: is parsed, the parser must recognize these as valid scenario headings
  - Each row in an Examples: table produces a separate Scenario entity that receives its own @id tag during sync, with placeholder substitution applied to step text
  - When a new scenario heading is encountered during step parsing, step collection for the current scenario must stop immediately — no step from one scenario may appear in another scenario's test function

  Constraints:
  - .feature files are the source of truth — beehave never modifies step text in .feature files
  - Parser completeness (QA7): when a .feature file uses Scenario Outline: or Scenario Template:, the parser recognizes and expands it; each Examples: row produces a separate scenario with its own @id
  - Step boundary integrity (QA9): when scenarios of different types are adjacent, steps do not leak across boundaries; each scenario's test function contains only its own step decorators
  - Idempotency: parsing a .feature file multiple times produces the same scenario list
  - Architecture decision AD1: prefix-based matching for _is_scenario_heading(), aligned with _is_section_break()'s existing prefix approach; section-break reset added to _parse_feature_steps()
  - MoSCoW: Must

  ## Changes

  | Session | Change |
  |---------|--------|
  | 2026-05-11 | Created: PP7 + PP9 — Scenario Outline/Template keyword recognition and step boundary integrity (shared root cause) |
  | 2026-05-11 | Break-down: split "recognize and expand" into 3 Rules (keyword recognition, Examples expansion, step boundary integrity); removed implementation-detail rules (already in AD1); merged duplicate boundary rules; 6 Must Examples |

  Rule: Scenario Outline and Template headings are recognized as valid scenario headings
    As a property-based TDD developer
    I want the parser to recognize Scenario Outline: and Scenario Template: as scenario headings
    So that parameterized scenarios are not invisible to the parser

    @id:7f3a9c2e
    Example: Scenario Outline is recognized as a scenario heading
      Given a .feature file containing "Scenario Outline: parameterized login"
      When the parser processes the file
      Then "parameterized login" appears in the parsed scenario list
      And the scenario is not skipped or ignored

    @id:b4e18d6f
    Example: Scenario Template is recognized as a scenario heading
      Given a .feature file containing "Scenario Template: data-driven withdrawal"
      When the parser processes the file
      Then "data-driven withdrawal" appears in the parsed scenario list
      And the scenario is not skipped or ignored

  Rule: Each Examples row produces a separate Scenario with its own @id tag
    As a QA engineer
    I want each Examples: row to produce a separate Scenario entity with its own @id tag
    So that each parameterized test case is independently traceable from .feature to test function

    @id:2c8f5a1d
    Example: Two Examples rows produce two separate scenarios with distinct @id tags
      Given a .feature file with "Scenario Outline: parameterized login" and an Examples table with 2 rows
      When the parser expands the scenario outline
      Then 2 separate Scenario entities are produced
      And each has a distinct @id tag
      And placeholder values from each row are substituted into step text

    @id:9e6b3f7a
    Example: A single-row Examples table produces one scenario with its own @id
      Given a .feature file with "Scenario Outline: edge case" and an Examples table with 1 row
      When the parser expands the scenario outline
      Then 1 Scenario entity is produced with its own @id tag
      And the placeholder value from the single row is substituted into step text

  Rule: Steps do not leak across scenario boundaries
    As a property-based TDD developer
    I want each scenario's test function to contain only its own steps
    So that validation and traceability operate on correct, self-contained scenario data

    @id:d1a4c8e2
    Example: Steps from a regular Scenario do not leak into an adjacent Scenario Outline
      Given a .feature file with "Scenario: first" followed by "Scenario Outline: second"
      And "Scenario: first" has Given/When/Then steps "setup first", "action first", "result first"
      And "Scenario Outline: second" has Given/When/Then steps "setup second", "action second", "result second"
      When the parser processes both scenarios
      Then "Scenario: first" contains only "setup first", "action first", "result first"
      And "Scenario Outline: second" contains only "setup second", "action second", "result second"

    @id:5f2d7b9c
    Example: Steps from a Scenario Outline do not leak into an adjacent regular Scenario
      Given a .feature file with "Scenario Outline: parameterized" followed by "Scenario: standalone"
      And "Scenario Outline: parameterized" has Given/When/Then steps "param setup", "param action", "param result"
      And "Scenario: standalone" has Given/When/Then steps "solo setup", "solo action", "solo result"
      When the parser processes both scenarios
      Then "Scenario Outline: parameterized" contains only "param setup", "param action", "param result"
      And "Scenario: standalone" contains only "solo setup", "solo action", "solo result"
