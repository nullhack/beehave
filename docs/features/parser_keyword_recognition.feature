Feature: Parser Keyword Recognition

  The Gherkin parser must recognize all Gherkin-6 scenario heading keywords (Scenario Outline:, Scenario Template:) and enforce step boundary integrity so that steps never leak across scenario boundaries. This feature addresses PP7 (scenario outlines invisible to the parser) and PP9 (steps leak into adjacent scenarios), which share a root cause: missing keyword recognition in _is_scenario_heading() and missing section-break reset logic in _parse_feature_steps().

  Rules (Business):
  - When a .feature file containing Scenario Outline: or Scenario Template: is parsed, the parser must recognize these as valid scenario headings and expand each Examples: row into a separate Scenario with placeholder substitution
  - When a new scenario heading is encountered during step parsing, step collection for the current scenario must stop immediately — no step from one scenario may appear in another scenario's test function
  - _is_scenario_heading() must use prefix-based matching (lines starting with "Scenario" or "Example") to cover all current and future Gherkin keyword variants
  - _parse_feature_steps() must reset current_id to None at every section break, preventing step accumulation across scenario boundaries
  - Each row in an Examples: table produces a separate Scenario entity that receives its own @id tag during sync
  - A Scenario's steps must never include steps from a different scenario — boundary integrity is a structural invariant of the FeatureScenario aggregate
  - The parser can recognize Scenario Outline: and Scenario Template: headings when the line starts with the canonical Gherkin heading prefixes "Scenario" or "Example"

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
