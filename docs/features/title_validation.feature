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

    Scenario: single valid file
      Given a feature file "docs/features/hive_activity.feature"
      And the feature has title "Hive Activity"
      And the feature has rule "Hive defense"
      And the rule has scenario "guard bee inspects visitor"
      When validate_all_titles is called
      Then the violation list is empty

    Scenario: two files with valid unique titles
      Given a feature file "docs/features/hive_activity.feature"
      And the feature has title "Hive Activity"
      And the feature has rule "Hive defense"
      And the rule has scenario "guard bee inspects visitor"
      And a feature file "docs/features/comb_construction.feature"
      And the feature has title "Comb Construction"
      And the feature has rule "Wax Production"
      And the rule has scenario "worker builds hexagonal cells"
      When validate_all_titles is called
      Then the violation list is empty

    Scenario: minimum word count title
      Given a feature file "docs/features/minimal.feature"
      And the feature has title "Minimal Title"
      And the feature has scenario "simple test"
      When validate_all_titles is called
      Then the violation list is empty

    Scenario: maximum word count title
      Given a feature file "docs/features/long_title.feature"
      And the feature has title "Long Title Feature"
      And the feature has scenario "worker bee deposits nectar into wax cell"
      When validate_all_titles is called
      Then the violation list is empty

  Rule: Title Charset Is Validated
    When any Feature, Rule, or Scenario title contains characters outside the
    valid charset — word characters, digits, and spaces only — then
    validate_all_titles produces a violation whose error_type reflects the
    title kind: invalid-feature-title, invalid-rule-title, or
    invalid-scenario-title.

    Scenario: feature title with hyphen
      Given a feature file "docs/features/bad_title.feature"
      And the feature has title "Hive-Activity"
      When validate_all_titles is called
      Then the violation list has 1 violation
      And the violation has error_type "invalid-feature-title"
      And the violation message indicates invalid characters

    Scenario: rule title with period
      Given a feature file "docs/features/bad_rule.feature"
      And the feature has title "Period Rule"
      And the feature has rule "Guard.Inspection"
      When validate_all_titles is called
      Then the violation list has 1 violation
      And the violation has error_type "invalid-rule-title"

    Scenario: scenario title with slash
      Given a feature file "docs/features/bad_scenario.feature"
      And the feature has title "Forward Slash Scenario"
      And the feature has scenario "guard/bee/inspects"
      When validate_all_titles is called
      Then the violation list has 1 violation
      And the violation has error_type "invalid-scenario-title"

    Scenario: underscore is valid charset
      Given a feature file "docs/features/underscore.feature"
      And the feature has title "Login_Flow"
      And the feature has scenario "user signs in with email"
      When validate_all_titles is called
      Then the violation list is empty

  Rule: Title Word Count Is Validated
    When any Feature, Rule, or Scenario title has fewer than 2 or more than 6
    words — counted by splitting on whitespace after stripping the Gherkin
    keyword prefix — then validate_all_titles produces a violation whose
    error_type reflects the title kind.

    Scenario: feature title has one word
      Given a feature file "docs/features/single_word.feature"
      And the feature has title "Activity"
      When validate_all_titles is called
      Then the violation list has 1 violation
      And the violation has error_type "invalid-feature-title"
      And the violation message indicates word count

    Scenario: rule title has seven words
      Given a feature file "docs/features/seven_words.feature"
      And the feature has title "Seven Word Rule"
      And the feature has rule "the guards respond to all unknown visitor bees"
      When validate_all_titles is called
      Then the violation list has 1 violation
      And the violation has error_type "invalid-rule-title"

    Scenario: scenario title is empty string
      Given a feature file "docs/features/empty_scenario.feature"
      And the feature has title "Empty Scenario"
      And the feature has scenario ""
      When validate_all_titles is called
      Then the violation list has 1 violation
      And the violation has error_type "invalid-scenario-title"

  Rule: Duplicate Titles Are Detected
    When any two titles across all feature files are case-insensitively equal
    — comparing Feature against Feature, Feature against Rule, Feature against
    Scenario, Rule against Rule, Rule against Scenario, and Scenario against
    Scenario — then validate_all_titles produces a violation for each duplicate
    whose error_type reflects the title kind: duplicate-feature-title,
    duplicate-rule-title, or duplicate-scenario-title.

    Scenario: duplicate feature titles
      Given a feature file "docs/features/hive_activity.feature"
      And the feature has title "Hive Activity"
      And the feature has scenario "guard bee inspects visitor"
      And a feature file "docs/features/hive_dup.feature"
      And the feature has title "hive activity"
      And the feature has scenario "forager returns with nectar"
      When validate_all_titles is called
      Then the violation list has 2 violations
      And one violation has error_type "duplicate-feature-title" for file "hive_activity.feature"
      And one violation has error_type "duplicate-feature-title" for file "hive_dup.feature"

    Scenario: rule matches feature title
      Given a feature file "docs/features/rule_feat.feature"
      And the feature has title "Hive Activity"
      And the feature has rule "Hive Activity"
      And the rule has scenario "guard bee inspects visitor"
      When validate_all_titles is called
      Then the violation list has 1 violation
      And the violation has error_type "duplicate-rule-title"

    Scenario: scenario matches feature title
      Given a feature file "docs/features/scenario_feat.feature"
      And the feature has title "Guard Inspection"
      And the feature has scenario "guard inspection"
      When validate_all_titles is called
      Then the violation list has 1 violation
      And the violation has error_type "duplicate-scenario-title"

    Scenario: scenario matches rule title
      Given a feature file "docs/features/scenario_rule.feature"
      And the feature has title "Hive Activity"
      And the feature has rule "Foraging Patterns"
      And the rule has scenario "Foraging Patterns"
      When validate_all_titles is called
      Then the violation list has 1 violation
      And the violation has error_type "duplicate-scenario-title"

    Scenario: duplicate scenarios
      Given a feature file "docs/features/dup_scenarios.feature"
      And the feature has title "Hive Activity"
      And the feature has scenario "guard bee inspects visitor"
      And the feature has scenario "Guard Bee Inspects Visitor"
      When validate_all_titles is called
      Then the violation list has 2 violations
      And both violations have error_type "duplicate-scenario-title"

    Scenario: mixed violation types
      Given a feature file "docs/features/mixed.feature"
      And the feature has title "Hive-Activity"
      And the feature has rule "Hive Activity"
      And the rule has scenario "forager returns with nectar"
      And a feature file "docs/features/other.feature"
      And the feature has title "Hive Activity"
      And the feature has scenario "other scenario"
      When validate_all_titles is called
      Then the violation list has 2 violations
      And one violation has error_type "invalid-feature-title"
      And one violation has error_type "duplicate-rule-title"

  Rule: Title Violations Included In Check
    When the `beehave check` command invokes check_all, title validation
    violations from validate_all_titles must be included in the result
    alongside scenario-level violations. Title violations are non-warning
    errors and contribute to exit code 1.

    Scenario: check includes title and scenario violations
      Given a feature file "docs/features/bad_title.feature"
      And the feature has title "Bad-Title"
      And the feature has scenario "simple scenario"
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

    Scenario: preflight blocks generation
      Given a feature file "docs/features/hive_activity.feature"
      And the feature has title "Hive Activity"
      And the feature has scenario "guard bee inspects visitor"
      And a feature file "docs/features/seven_words.feature"
      And the feature has title "seven word title feature file name"
      And the feature has scenario "some scenario"
      When generate_stubs is called for "hive_activity.feature"
      Then the process exits with exit code 1
      And the output contains a violation for "seven word title feature file name"
      And no test files or directories are created for hive_activity.feature
