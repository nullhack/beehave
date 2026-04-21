Feature: Multilingual feature parsing
  Parses .feature files written in any language supported by gherkin-official. Non-English parsing
  is triggered by the standard `# language: xx` comment in the feature file. Function names are
  derived from the feature folder name, never from Gherkin keywords, so any language works
  transparently without any beehave configuration.

  Status: BASELINED (2026-04-18)

  Rules (Business):
  - The `# language: xx` comment is the sole mechanism for non-English parsing; no beehave config needed.
  - Function names and class names are derived from the feature folder name, never from Gherkin keywords.
  - Each .feature file is parsed independently; mixed-language projects work transparently.

  Constraints:
  - No pyproject.toml language configuration — out of scope.
  - No custom error handling for unrecognised language codes — out of scope.
  - No keyword normalisation to English in docstrings.
  - No implementation changes to feature_parser.py expected; tests prove existing behaviour.

  Rule: Spanish feature file parsing
    As a developer working on a Spanish-language project
    I want my Spanish Gherkin feature files to be parsed correctly
    So that the plugin does not break on non-English files

    @id:e1081346
    Example: A valid Spanish Gherkin feature file is parsed without error
      Given a valid Spanish Gherkin feature file
      When parse_feature is called on that file
      Then a ParsedFeature is returned with the correct number of examples

  Rule: Chinese feature file parsing
    As a developer working on a Chinese-language project
    I want my Chinese Gherkin feature files to be parsed correctly
    So that the plugin does not break on non-English files

    @id:55e4d669
    Example: A valid Chinese Gherkin feature file is parsed without error
      Given a valid Chinese Gherkin feature file
      When parse_feature is called on that file
      Then a ParsedFeature is returned with the correct number of examples

  Rule: Mixed-language project compatibility
    As a developer on a project with feature files in multiple languages
    I want all feature files to be parsed correctly in a single sync run
    So that language choice per file does not affect the rest of the project

    @id:3c04262e
    Example: Spanish and English feature files coexist in the same project without conflict
      Given a project containing a valid Spanish Gherkin feature file and a valid English feature file
      When parse_feature is called on each file independently
      Then both files are parsed successfully and return valid ParsedFeature objects
