Feature: Universal Parameterization

  Plain Scenario: blocks should support <placeholder> syntax for variables without requiring Scenario Outline. When <placeholder> appears in a plain Scenario's step text, the parser extracts it as a variable. Hypothesis generates values from strategy resolution. The '<name>' (single-quoted) pattern forces string type. This stays Gherkin-compatible — <placeholder> is valid text in any scenario context.

  This feature addresses PP15: developers cannot parameterize plain scenarios without rewriting them as Scenario Outline, creating friction when evolving concrete scenarios.

  Rules (Business):
  - When a plain Scenario: block contains <placeholder> syntax in step text, the parser extracts placeholders
  - Generated test stubs include function parameters matching <placeholder> names, and Hypothesis generates values from strategy resolution at test runtime
  - When <placeholder> is wrapped in single quotes ('<name>'), the strategy resolution forces string type regardless of module-level variable type

  Constraints:
  - .feature files are the source of truth — beehave never modifies step text in .feature files
  - Universal parameterization (QA15): when a plain Scenario: uses <placeholder> syntax, variables are extracted and test stubs are generated with parameters
  - Strategy resolution: module-level variable lookup by name; fallback to st.integers() with UserWarning
  - Gherkin compatibility: <placeholder> is valid text in any Gherkin scenario context; Examples tables are only valid under Scenario Outline/Template, NOT plain Scenario
  - Architecture decision AD5: universal parameterization via <placeholder> in any scenario type; '<name>' forces string type
  - MoSCoW: Should

  ## Changes

  | Session | Change |
  |---------|--------|
  | 2026-05-11 | Created: PP15 — Universal parameterization for plain Scenario: blocks |

  Rule: Plain Scenario steps with <placeholder> extract variables regardless of scenario type
    As a property-based TDD developer
    I want the parser to extract <placeholder> patterns from any scenario's step text, not just Scenario Outline
    So that I can parameterize simple scenarios without rewriting them

    @id:6f8d808c
    Example: A plain Scenario with <name> in step text extracts the placeholder
      Given a .feature file with "Scenario: simple bee" and step "Given a bee named <bee_name> with <frames> frames"
      When the parser processes the file
      Then the scenario has placeholders ["bee_name", "frames"]

    @id:955893de
    Example: A plain Scenario without <placeholder> has no placeholders extracted
      Given a .feature file with "Scenario: static test" and step "Given a bee named zoom"
      When the parser processes the file
      Then the scenario has no placeholders

  Rule: Generated stubs include function parameters for placeholders without Examples table
    As a property-based TDD developer
    I want generated test stubs to have function parameters matching <placeholder> names when no Examples table is present
    So that Hypothesis generates values from strategy resolution at runtime

    @id:794a895b
    Example: Stub for plain Scenario with <placeholder> has function parameters
      Given a .feature file with "Scenario: bee flight" and step "Given a bee flies <distance> meters"
      And no Examples table
      When beehave generate creates the test stub
      Then the test function has parameter "distance"
      And the @given decorator uses strategy resolution for "distance"

    @id:c4c97662
    Example: Stub for plain Scenario with multiple placeholders has all parameters
      Given a .feature file with "Scenario: hive health" with steps containing <colony_size> and <nectar_units>
      And no Examples table
      When beehave generate creates the test stub
      Then the test function has parameters ["colony_size", "nectar_units"]

  Rule: Single-quoted placeholder forces string type
    As a property-based TDD developer
    I want '<name>' (single-quoted) to force string type in strategy resolution
    So that I can explicitly declare string variables without relying on type inference

    @id:a22d6bd3
    Example: '<name>' in step text forces string strategy
      Given a .feature file with step "Given a bee named '<bee_name>'"
      When the parser extracts placeholders
      Then "bee_name" is marked as string type
      And strategy resolution uses st.text() instead of module-level variable lookup

    @id:1c2d3e4f
    Example: Unquoted <name> uses normal strategy resolution
      Given a .feature file with step "Given <frames> frames"
      When the parser extracts placeholders
      Then "frames" uses normal strategy resolution (module-level variable lookup, fallback st.integers())
