Feature: hatch — generate demo .feature files

  Generates one or two bee-themed demo .feature files covering the most common Gherkin patterns
  (Feature, Rule, Example, Scenario Outline). The files are ready for beehave sync to process,
  so a developer can immediately experience the full sync workflow end-to-end without writing
  their own .feature content first.

  Status: ELICITING

  Rules (Business):
  - hatch never overwrites an existing .feature file
  - Generated files cover: Feature header, Rule block, plain Example, Scenario Outline

  Constraints:
  - Demo content is bee-themed (vocabulary consistent with beehave branding)
