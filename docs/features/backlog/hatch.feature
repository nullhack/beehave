Feature: hatch — generate demo .feature files

  Generates one or two bee-themed demo .feature files covering the most common Gherkin patterns
  (Feature, Rule, Example, Scenario Outline). The files are ready for beehave sync to process,
  so a developer can immediately experience the full sync workflow end-to-end without writing
  their own .feature content first.

  Status: BASELINED (2026-04-22)

  Rules (Business):
  - hatch never overwrites an existing .feature file
  - Generated files cover: Feature header, Rule block, plain Example, Scenario Outline

  Constraints:
  - Demo content is bee-themed (vocabulary consistent with beehave branding)

  Rule: Demo file generation
    As a new beehave user
    I want hatch to generate ready-to-use demo .feature files
    So that I can see beehave sync working end-to-end without writing my own content first

    @id:5e6028ce
    Example: hatch creates at least one .feature file in the features_dir
      Given an empty docs/features/backlog/ directory
      When beehave hatch runs
      Then at least one .feature file exists in docs/features/backlog/

    @id:4e364a9d
    Example: Generated .feature file contains a Rule block
      Given beehave hatch has run
      When the generated .feature file is inspected
      Then it contains at least one Rule: block with a user story

    @id:c452ac34
    Example: Generated .feature file contains a plain Example
      Given beehave hatch has run
      When the generated .feature file is inspected
      Then it contains at least one Example: block with Given/When/Then steps

    @id:9979040f
    Example: Generated .feature file contains a Scenario Outline
      Given beehave hatch has run
      When the generated .feature file is inspected
      Then it contains at least one Scenario Outline: block with an Examples table

  Rule: No-overwrite safety
    As a developer
    I want hatch to never overwrite an existing .feature file
    So that running it on an existing project does not destroy my work

    @id:24514455
    Example: Existing .feature file is not overwritten
      Given a .feature file already exists in docs/features/backlog/
      When beehave hatch runs
      Then the existing file content is unchanged

    @id:def76ef7
    Example: hatch reports skipped files when a target file already exists
      Given a target demo .feature file already exists
      When beehave hatch runs
      Then beehave reports that the file was skipped rather than overwritten

  Rule: Bee-themed content
    As a new beehave user
    I want the demo content to use bee-themed vocabulary
    So that the examples are memorable and consistent with the beehave brand

    @id:a81d2b1c
    Example: Generated .feature file uses bee-themed domain vocabulary
      Given beehave hatch has run
      When the generated .feature file is inspected
      Then the feature name and step text use bee-related domain terms
