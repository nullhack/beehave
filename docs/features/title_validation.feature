Feature: Title Validation

  The `validate_all_titles(config)` function reads all `.feature` files from
  the project's features directory and validates every Feature, Rule, and
  Scenario title for charset (word characters, digits, spaces only), word
  count (2–6 words after stripping the Gherkin keyword prefix), and global
  case-insensitive uniqueness across all three title types. It returns a
  list of Violation objects — one per invalid or duplicate title — or an
  empty list when all titles are valid.

  Serves the Feature Parsing bounded context. Called by `check_all()` in
  Consistency Checking and `generate_stubs()` pre-flight in Code Generation.
  Violation types: invalid-feature-title, invalid-rule-title,
  invalid-scenario-title, duplicate-feature-title, duplicate-rule-title,
  duplicate-scenario-title.

  # Constraints:
  # Technology:
  # - gherkin-official library for AST parsing: grep import gherkin_official
  # - Regular expressions for token extraction: grep re.compile
  # - Title validation across all .feature files: grep validate_all_titles
  # Quality:
  # - Correctness: Title validation is deterministic — given identical
  #   feature files, validate_all_titles always produces the same violations.
  # - Reliability: GherkinError in any file is raised immediately with zero
  #   partial output — no violations are returned when a parse error occurs.
  # - Simplicity: validate_all_titles makes a single pass over all feature
  #   files, extracting only titles via lightweight AST traversal.

  Background:
    Given a project with features directory "docs/features"
    And a config with features_dir set to "docs/features"

  Rule: Valid Titles Produce No Violations
    When all feature files across the project contain Feature, Rule, and Scenario
    titles that match the charset `[\w\s]+`, have 2–6 words after Gherkin keyword
    stripping, and are globally unique (case-insensitive), then
    validate_all_titles returns an empty list — zero violations.

    Scenario: single file with all valid titles
      Given a feature file "docs/features/hive_activity.feature" with
        Feature title "Hive Activity"
        And Rule title "Hive defense"
        And Scenario title "guard bee inspects visitor"
      When validate_all_titles is called
      Then the violation list is empty

    Scenario: two files with unique titles across feature rule and scenario types
      Given a feature file "docs/features/hive_activity.feature" with
        Feature title "Hive Activity"
        And Rule title "Hive defense"
        And Scenario title "guard bee inspects visitor"
      And a feature file "docs/features/comb_construction.feature" with
        Feature title "Comb Construction"
        And Rule title "Wax Production"
        And Scenario title "worker builds hexagonal cells"
      When validate_all_titles is called
      Then the violation list is empty

    Scenario: title with exactly two words at lower boundary
      Given a feature file with Feature title "Minimal Title"
      And Scenario title "simple scenario test"
      When validate_all_titles is called
      Then the violation list is empty

    Scenario: title with exactly six words at upper boundary
      Given a feature file with Feature title "Long Title Feature"
      And Scenario title "worker bee deposits nectar into wax cell"
      When validate_all_titles is called
      Then the violation list is empty

  Rule: Title Charset Is Validated
    When any Feature, Rule, or Scenario title contains characters outside the
    valid charset — Unicode letters, digits, and spaces only — then
    validate_all_titles produces a violation whose error_type reflects the
    title kind: invalid-feature-title, invalid-rule-title, or
    invalid-scenario-title.

    Scenario: feature title contains a hyphen
      Given a feature file with Feature title "Hive-Activity"
      When validate_all_titles is called
      Then the violation list has 1 violation
      And the violation has error_type "invalid-feature-title"
      And the violation message indicates invalid characters

    Scenario: rule title contains a period
      Given a feature file with Feature title "Period Rule"
      And Rule title "Guard.Inspection"
      When validate_all_titles is called
      Then the violation list has 1 violation
      And the violation has error_type "invalid-rule-title"

    Scenario: scenario title contains a forward slash
      Given a feature file with Feature title "Forward Slash Scenario"
      And Scenario title "guard/bee/inspects"
      When validate_all_titles is called
      Then the violation list has 1 violation
      And the violation has error_type "invalid-scenario-title"

  Rule: Title Word Count Is Validated
    When any Feature, Rule, or Scenario title has fewer than 2 or more than 6
    words — counted by splitting on whitespace after stripping the Gherkin
    keyword prefix — then validate_all_titles produces a violation whose
    error_type reflects the title kind.

    Scenario: feature title has only one word
      Given a feature file with Feature title "Activity"
      When validate_all_titles is called
      Then the violation list has 1 violation
      And the violation has error_type "invalid-feature-title"
      And the violation message indicates word count

    Scenario: rule title has seven words
      Given a feature file with Feature title "Seven Word Rule"
      And Rule title "the guards respond to all unknown visitor bees"
      When validate_all_titles is called
      Then the violation list has 1 violation
      And the violation has error_type "invalid-rule-title"

    Scenario: scenario title is empty after keyword strip
      Given a feature file with Feature title "Empty Scenario"
      And Scenario title ""
      When validate_all_titles is called
      Then the violation list has 1 violation
      And the violation has error_type "invalid-scenario-title"

  Rule: Duplicate Titles Are Detected
    When any two titles across all feature files are case-insensitively equal
    — comparing Feature against Feature, Feature against Rule, Feature against
    Scenario, Rule against Rule, Rule against Scenario, and Scenario against
    Scenario — then validate_all_titles produces a violation for each duplicate
    whose error_type reflects the tile kind: duplicate-feature-title,
    duplicate-rule-title, or duplicate-scenario-title.

    Scenario: two features with case insensitive duplicate feature titles
      Given a feature file "docs/features/hive_activity.feature" with
        Feature title "Hive Activity"
        And Scenario title "guard bee inspects visitor"
      And a feature file "docs/features/hive_activity_duplicate.feature" with
        Feature title "hive activity"
        And Scenario title "forager returns with nectar"
      When validate_all_titles is called
      Then the violation list has 2 violations
      And one violation has error_type "duplicate-feature-title" for file "hive_activity.feature"
      And one violation has error_type "duplicate-feature-title" for file "hive_activity_duplicate.feature"

    Scenario: rule title matches feature title
      Given a feature file with Feature title "Hive Activity"
      And Rule title "Hive Activity"
      And Scenario title "guard bee inspects visitor"
      When validate_all_titles is called
      Then the violation list has 1 violation
      And the violation has error_type "duplicate-rule-title"

    Scenario: scenario title matches feature title case insensitively
      Given a feature file with Feature title "Guard Inspection"
      And Scenario title "guard inspection"
      When validate_all_titles is called
      Then the violation list has 1 violation
      And the violation has error_type "duplicate-scenario-title"

    Scenario: scenario title matches rule title
      Given a feature file with Feature title "Hive Activity"
      And Rule title "Foraging Patterns"
      And Scenario title "Foraging Patterns"
      When validate_all_titles is called
      Then the violation list has 1 violation
      And the violation has error_type "duplicate-scenario-title"

    Scenario: two scenarios with case insensitive duplicate
      Given a feature file with Feature title "Hive Activity"
      And Scenario title "guard bee inspects visitor"
      And Scenario title "Guard Bee Inspects Visitor"
      When validate_all_titles is called
      Then the violation list has 2 violations
      And both violations have error_type "duplicate-scenario-title"

    Scenario: multiple violation types in one validation pass
      Given a feature file "docs/features/mixed_issues.feature" with
        Feature title "Hive-Activity"
        And Rule title "Hive Activity"
        And Scenario title "forager returns with nectar"
      And a feature file "docs/features/other.feature" with
        Feature title "Hive Activity"
        And Scenario title "other scenario"
      When validate_all_titles is called
      Then the violation list has 3 violations
      And one violation has error_type "invalid-feature-title"
      And one violation has error_type "duplicate-rule-title"
      And one violation has error_type "duplicate-feature-title"

  Rule: Title Violations Included In Check
    When the `beehave check` command invokes check_all, title validation
    violations from validate_all_titles must be included in the result
    alongside scenario-level violations. Title violations are non-warning
    errors and contribute to exit code 1.

    Scenario: check all includes title charset violation with scenario violations
      Given a feature file "docs/features/bad_title.feature" with
        Feature title "Bad-Title"
        And Scenario title "simple scenario"
      And no matching test file exists for "bad_title"
      When check_all is called
      Then the violation list contains an invalid-feature-title violation for "Bad-Title"
      And the violation list contains an unmapped-scenario violation for "simple scenario"
      And all title violations are errors with is_warning false

  Rule: Title Validation Blocks Generation
    When the `beehave generate` command invokes generate_stubs, title
    validation must run as a pre-flight check before any file writes.
    If any .feature file in the project has an invalid or duplicate title,
    generation is refused with exit code 1, all violations are printed,
    and zero partial output is written to disk.

    Scenario: pre flight fails when any feature has title violation
      Given a feature file "docs/features/hive_activity.feature" with
        Feature title "Hive Activity"
        And Scenario title "guard bee inspects visitor"
      And a feature file "docs/features/seven_words.feature" with
        Feature title "seven word title feature file name"
        And Scenario title "some scenario"
      When generate_stubs is called for "hive_activity.feature"
      Then the process exits with exit code 1
      And the output contains a violation for "seven word title feature file name"
      And no test files or directories are created for hive_activity.feature
