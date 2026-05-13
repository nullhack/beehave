Feature: Step Ordering and Placeholder Validation

  beehave validates step ordering (Given → When → Then), placeholder-parameter matching, and supports progressive adoption levels.

  Rules (Business):
  - Step ordering must follow Given → When → Then; @And/@But inherit from the preceding step type
  - Every <placeholder> name in step text must appear as a function parameter
  - Tests without .feature files operate at adoption level 1 with limited validation

  Constraints:
  - Validation is collection-time (CLI commands) — zero runtime overhead on passing tests
  - Tests at adoption level 1 skip .feature-dependent checks

  ## Changes

  | Session | Change |
  |---------|--------|
  | 2026-05-11 | Split from feature_parsing_validation per stakeholder approval |
  | 2026-05-11 | Added @And/@But ordering examples, reconciled adoption levels |

  Rule: Step ordering validation ensures Given before When before Then
    As a developer
    I want beehave to validate that my step decorators follow Gherkin ordering
    So that my tests have correct structure even without .feature files

    @id:9f5d3b2a
    Example: Valid step ordering passes validation
      Given a test with decorators @Given, @When, @Then in order
      When beehave validates step ordering
      Then no ordering violation is reported

    @id:1c8e4a7d
    Example: Invalid step ordering fails validation
      Given a test with decorators @Then, @Given, @When (out of order)
      When beehave validates step ordering
      Then an ordering violation is reported

    @id:b7e2f1a4
    Example: @And/@But inherit preceding step type for ordering
      Given a test with decorators @Given, @And, @When, @And, @Then, @But in order
      When beehave validates step ordering
      Then no ordering violation is reported

  Rule: Placeholder names must match function parameters
    As a developer
    I want beehave to validate that every <placeholder> in step text appears as a function parameter
    So that strategy resolution and @Example mapping work correctly

    @id:5b7f2d9e
    Example: All placeholders match function parameters
      Given a step "a user with balance <initial>" and a function with parameter initial
      When beehave validates placeholders
      Then no mismatch is reported

    @id:d3a6c1b8
    Example: Missing function parameter for placeholder
      Given a step "a user with balance <initial>" and a function with no initial parameter
      When beehave validates placeholders
      Then a mismatch is reported: "<initial> not found in function parameters"

  Rule: Progressive adoption allows validation at different levels
    As a developer
    I want to adopt beehave incrementally without requiring .feature files on day one
    So that I can start with decorators only and add traceability later

    @id:8e2f7c4a
    Example: Level 1 — decorators only, no .feature file
      Given a test with @Given, @When, @Then decorators but no .feature file
      When beehave validates the test
      Then step ordering is validated
      And placeholder-parameter matching is validated
      But step text matching is not validated (no .feature file)
      And @id traceability is not validated (no .feature file)

    @id:a4d9b3e6
    Example: Level 2 — decorators with @id traceability
      Given a test with @Given, @When, @Then decorators and a .feature file with matching @id
      When beehave validates the test
      Then step text matching is validated against .feature
      And @id traceability is validated
      And orphan detection is active
