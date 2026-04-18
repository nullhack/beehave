Feature: Multilingual feature parsing
  As a developer
  I want pytest-beehave to parse .feature files written in any language supported by gherkin-official
  So that non-English projects work transparently without any beehave configuration

  Discovery:

  Status: BASELINED (2026-04-18)

  Entities:
  | Type | Name | Candidate Class/Method | In Scope |
  |------|------|----------------------|----------|
  | Noun | `.feature` file | Gherkin feature file on disk | Yes |
  | Noun | `# language: xx` comment | Language directive at top of feature file | Yes |
  | Noun | non-English keyword | Gherkin keyword in a supported dialect | Yes |
  | Noun | feature slug | Underscored folder name used in Python identifiers | Yes |
  | Noun | docstring | Step-by-step docstring in generated test stub | Yes |
  | Noun | pyproject.toml language config | Project-level default language setting | No |
  | Noun | bad language code error handling | Custom error for unrecognised language codes | No |

  Rules (Business):
  - The `# language: xx` comment is the sole mechanism for non-English parsing; no beehave config needed.
  - Function names and class names are derived from the feature folder name, never from Gherkin keywords.
  - Each .feature file is parsed independently; mixed-language projects work transparently.

  Constraints:
  - No pyproject.toml language configuration — out of scope.
  - No custom error handling for unrecognised language codes — out of scope.
  - No keyword normalisation to English in docstrings.
  - No implementation changes to feature_parser.py expected; tests prove existing behaviour.

  Session 1 — Individual Entity Elicitation:
  | ID | Question | Answer | Status |
  |----|----------|--------|--------|
  | Q1 | Should beehave support a project-level default language? | No — transparent; # language: xx is the only mechanism | ANSWERED |
  | Q2 | Which languages need verification? | Spanish (es) and Chinese Simplified (zh-CN) | ANSWERED |
  | Q3 | Custom error handling for bad language codes? | No — out of scope | ANSWERED |
  | Q4 | Mixed-language projects work transparently? | Yes — each file parsed independently | ANSWERED |
  | Q5 | Docstrings normalise non-English keywords to English? | No — preserve original keyword | ANSWERED |
  | Q6 | Scope? | Tests only — verify existing behaviour | ANSWERED |
  Template §1: CONFIRMED
  Synthesis: pytest-beehave is transparent to Gherkin language. The gherkin-official library auto-detects
  the # language: xx comment and switches keyword matching accordingly. Function names and class names
  are always derived from the feature folder name (a filesystem path), so they are valid Python identifiers
  regardless of the .feature file language. Docstrings preserve the original non-English keywords.
  Mixed-language projects work because each file is parsed independently.

  Session 2 — Behavior Groups / Big Picture:
  Template §2: CONFIRMED
  Behavior Groups:
  - Spanish parsing: A .feature file with # language: es and Spanish keywords parses correctly and produces stubs with Spanish keywords in docstrings.
  - Chinese parsing: A .feature file with # language: zh-CN and Chinese keywords parses correctly and produces stubs with Chinese keywords in docstrings.
  - Mixed-language project: A project containing both Spanish and English .feature files parses all files correctly in one sync run.
  - Python identifier safety: Function names and class names derived from folder names are always valid Python identifiers, unaffected by the .feature file language.

  Session 3 — Feature Synthesis:
  Synthesis: pytest-beehave delegates all language handling to gherkin-official. When a .feature file
  begins with # language: es, the parser switches to Spanish keywords (Característica:, Dado:, Cuando:,
  Entonces:, etc.) automatically. When it begins with # language: zh-CN, it switches to Chinese keywords
  (功能:, 假设:, 当:, 那么:, etc.). The plugin never inspects the language directive itself. Generated
  test stubs use the feature folder name for function/class names (always ASCII-safe slugs), and preserve
  the original keyword text verbatim in docstrings. A project with mixed-language .feature files works
  because each file is parsed in isolation.
  Template §3: CONFIRMED — stakeholder approved 2026-04-18

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
