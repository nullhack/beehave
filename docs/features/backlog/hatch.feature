Feature: Hatch — generate example/demo feature files
Status: BASELINED (2026-04-23)

`beehave hatch` generates one or two bee-themed demo `.feature` files covering
common Gherkin patterns (Feature, Rule, Example, Scenario Outline) so that
the user can immediately demo the full sync workflow end-to-end.

Rule: Hatch generates demo content

  @id:a7c702b7
  Example: Hatch creates bee-themed feature file
    Given a newly nested project with no `.feature` files
    When the user runs "beehave hatch"
    Then one or two bee-themed `.feature` files are created in `docs/features/`
    And each file demonstrates common Gherkin patterns: Feature, Rule, Example, and Scenario Outline

  @id:91b8e512
  Example: Hatch content enables full sync demo
    Given a project with hatch-generated `.feature` files
    When the user runs "beehave sync"
    Then stubs are generated for all Examples in the demo files
