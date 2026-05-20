Feature: Status Command

  The `beehave status` command computes and displays the development stage
  of every feature in the project by synthesizing parsed Gherkin scenarios,
  discovered test functions, and consistency violation data. Each feature
  receives a stage label ("broken", "no scenarios", "needs scenarios",
  "needs tests", "needs bodies", "needs fixes", or "ok") derived
  deterministically from disk state — no stored state, no caching.

  Serves the Status Reporting bounded context. Key entities: ScenarioStatus,
  FeatureStatus, StatusReport, OrphanedDir, Collision.

  # Constraints:
  # Technology:
  # - Feature parsing: from beehave.gherkin import parse_feature, detect_empty_rules
  # - Test discovery: from beehave.discover import discover_tests
  # - Consistency checking: from beehave.check import check_pair
  # - CLI integration: status subcommand in cli.py
  # Quality:
  # - Correctness: Stage derivation is deterministic — given identical disk state,
  #   the status command always produces the same stage for each feature.
  # - Reliability: Zero partial output. Parse errors produce "broken" stage, not
  #   a crash. The StatusReport always includes every feature in the features_dir.
  # - Simplicity: Status Reporting imports beehave internal modules (gherkin, discover,
  #   check) — it is a beehave command, not generated code.
  # - Composability: The --json output schema (features array, summary object,
  #   orphaned_directories, collisions) is stable within a major version for external
  #   tooling consumption.

  Background:
    Given a project with features directory "docs/features"
    And tests directory "tests/features"

  Rule: Parse Error Captured as Stage
    When a feature file contains invalid Gherkin syntax, the parse_feature() call raises GherkinError.
    The error must be caught and the feature stage must be "broken" with the error message captured
    in parse_error_message. No scenario details are populated for a broken feature.

    Scenario: feature missing colon after Scenario
      Given a feature file "docs/features/bad_scenario.feature" with content:
        """
        Feature: Bad Scenario
          Scenario bad title
            Given something
        """
      When the status command computes the feature status
      Then the feature stage is "broken"
      And parse_error_message contains "expected: #TagLine, #FeatureLine, #RuleLine, #Comment, #Empty"
      And scenarios_total is 0
      And the tree output shows the feature with label "broken"

    Scenario: feature with unrecognized Gherkin keyword
      Given a feature file "docs/features/unknown_keyword.feature" with content:
        """
        Feature: Unknown Keyword
          Situation: misnamed step
            Given something
        """
      When the status command computes the feature status
      Then the feature stage is "broken"
      And parse_error_message is not null
      And scenarios list is empty

  Rule: Empty Features Report No Scenarios
    When a feature file parses successfully into zero ScenarioInfo entries and detect_empty_rules()
    returns has_empty_rules=False, the status command reports stage "no scenarios" with all
    scenario counts at zero.

    Scenario: feature with title only and comment
      Given a feature file "docs/features/placeholder.feature" with content:
        """
        Feature: Placeholder
          # Work in progress — no scenarios yet
        """
      When the status command computes the feature status
      Then detect_empty_rules returns has_empty_rules=False
      And the feature stage is "no scenarios"
      And scenarios_total is 0
      And scenarios_ok is 0
      And scenarios_no_test is 0

    Scenario: feature with background but no scenarios
      Given a feature file "docs/features/bg_only.feature" with content:
        """
        Feature: Background Only
          Background:
            Given the system is initialized
        """
      When the status command computes the feature status
      Then detect_empty_rules returns has_empty_rules=False
      And the feature stage is "no scenarios"

  Rule: Rules Without Scenarios Detected
    When parse_feature() returns an empty dict and detect_empty_rules() returns has_empty_rules=True,
    the feature has Rule nodes with zero Scenario children. The status command must report
    stage "needs scenarios", distinct from "no scenarios".

    Scenario: feature with rules and no scenarios
      Given a feature file "docs/features/draft_rules.feature" with content:
        """
        Feature: Draft Rules
          Rule: Authentication rules
          Rule: Authorization rules
        """
      When the status command computes the feature status
      Then detect_empty_rules returns has_empty_rules=True
      And detect_empty_rules returns rule_titles with "Authentication rules", "Authorization rules"
      And the feature stage is "needs scenarios"
      And scenarios_total is 0

  Rule: Unmapped Scenarios Derive Stage
    When any scenario in a feature file has no matching test function in the discovered
    test files, its scenario status is "no test". The feature stage becomes "needs tests"
    regardless of the status of other scenarios.

    Scenario: feature with three scenarios one unmapped
      Given a feature file "docs/features/partial.feature" with 3 scenarios
      And the test file "tests/features/partial/default_test.py" has 2 matching test functions
      And test "test_scenario_three" has no matching function in the test file
      When the status command computes the feature status
      Then the scenario status of "test_scenario_three" is "no test"
      And the feature stage is "needs tests"
      And scenarios_total is 3
      And scenarios_no_test is 1

    Scenario: feature with all scenarios unmapped
      Given a feature file "docs/features/unmapped.feature" with 2 scenarios
      And no test file exists at "tests/features/unmapped/default_test.py"
      When the status command computes the feature status
      Then all scenario statuses are "no test"
      And the feature stage is "needs tests"
      And scenarios_no_test is 2

  Rule: All Stubs Derive Stage
    When every scenario in a feature is mapped to a test function, but ALL matched test
    functions are stubs (is_stub is True), the feature stage is "needs bodies". Stub detection
    follows the invariant: a body with only pass or Ellipsis is a stub.

    Scenario: feature scenarios all mapped to stubs
      Given a feature file "docs/features/stub_all.feature" with 3 scenarios
      And the test file "tests/features/stub_all/default_test.py" has 3 matching functions
      And every matching test function body is "..."
      When the status command computes the feature status
      Then all scenario statuses are "no body"
      And the feature stage is "needs bodies"
      And scenarios_no_body is 3
      And scenarios_ok is 0

    Scenario: feature with stub and non stub
      Given a feature file "docs/features/stub_mix.feature" with 2 scenarios
      And test "test_implemented" is non-stub with zero violations
      And test "test_not_implemented" is a stub with body "pass"
      When the status command computes the feature status
      Then scenario "test_implemented" status is "ok"
      And scenario "test_not_implemented" status is "no body"
      And the feature stage is "needs bodies"

  Rule: Violations Derive Stage
    When all scenarios are mapped to non-stub test functions, but check_pair() reports one
    or more violations (non-warning), the feature stage is "needs fixes". The {N} errors format
    is used for scenario status when violations are present.

    Scenario: feature scenario with missing literal
      Given a feature file "docs/features/missing_literal.feature" with 3 scenarios
      And test "test_payment_approval" has body constant nodes missing literal "approved"
      And the other 2 scenarios have zero violations
      When the status command computes the feature status
      Then scenario "test_payment_approval" status is "1 error"
      And its violations include missing-literal for "approved"
      And the feature stage is "needs fixes"
      And scenarios_errors is 1
      And scenarios_ok is 2

    Scenario: feature with multiple scenarios having violations
      Given a feature file "docs/features/multi_viol.feature" with 2 scenarios
      And test "test_login" has missing-placeholder violation for "username"
      And test "test_logout" has missing-literal violation for "session"
      When the status command computes the feature status
      Then the feature stage is "needs fixes"
      And scenarios_errors is 2

  Rule: All Passing Derives Ok
    When all scenarios in a feature are mapped to non-stub test functions and check_pair()
    returns zero violations for every pair, the feature stage is "ok".

    Scenario: feature with all scenarios passing
      Given a feature file "docs/features/fully_implemented.feature" with 3 scenarios
      And all 3 matching test functions are non-stub
      And check_pair returns empty violations for all pairs
      When the status command computes the feature status
      Then all scenario statuses are "ok"
      And the feature stage is "ok"
      And scenarios_ok is 3
      And scenarios_errors is 0

  Rule: Worst Scenario Wins
    The feature stage is derived by evaluating the Stage Decision Tree conditions in priority
    order (1 through 7). The first condition whose predicate is satisfied by any scenario
    determines the feature stage. This means the worst scenario status dictates the feature stage.

    Scenario: mixed feature with all scenario statuses
      Given a feature file "docs/features/mixed.feature" with 3 scenarios
      And scenario A is mapped to a non-stub test with zero violations
      And scenario B is mapped to a stub test
      And scenario C has no matching test function
      When the status command computes the feature status
      Then scenario A status is "ok"
      And scenario B status is "no body"
      And scenario C status is "no test"
      And the feature stage is "needs tests"

    Scenario: mixed feature ok and error scens
      Given a feature file "docs/features/ok_plus_errors.feature" with 2 scenarios
      And scenario A is mapped to a non-stub test with zero violations
      And scenario B is mapped to a non-stub test with missing-placeholder violation
      When the status command computes the feature status
      Then scenario A status is "ok"
      Then scenario B status is "1 error"
      And the feature stage is "needs fixes"

  Rule: Ok Feature Collapses in Output
    When a feature has stage "ok", the human-readable tree output must display it as a single
    line without expanding scenario details. The label is left-aligned in a fixed-width column
    followed by the feature slug and title in parentheses.

    Scenario: ok feature shown as tree line
      Given a StatusReport with one feature
      And the feature "fully_implemented" has stage "ok" and title "Fully Implemented"
      When the status command formats the human-readable tree output
      Then the output contains exactly one line for the feature
      And the line matches "ok            fully_implemented (Fully Implemented)"
      And no scenario lines appear beneath the feature heading

    Scenario: two ok features with blank separator
      Given a StatusReport with two features
      And feature "auth" has stage "ok" and title "Authentication"
      And feature "payment" has stage "ok" and title "Payment"
      When the status command formats the human-readable tree output
      Then the output shows "auth" on one line and "payment" on the next line
      And a blank line separates the two feature blocks

  Rule: Tree Output Shows Rule Hierarchy
    When a non-ok feature contains Rules, the tree output must display each Rule as an
    intermediate hierarchy node. Rule nodes show an aggregated label derived from the worst
    child scenario statuses with counts. Tree-drawing characters (├──, └──, │) connect
    parent feature to child rules and scenarios.

    Scenario: feature rules shown in tree output
      Given a feature file "docs/features/ecommerce.feature" with 2 Rules
      And Rule "Cart operations" has scenarios with statuses: ok, ok, no body
      And Rule "Checkout flow" has scenarios with statuses: 2 errors, ok
      When the status command formats the human-readable tree output
      Then the feature heading shows stage "needs fixes"
      And Rule "Cart operations" shows aggregation "1 no body"
      And Rule "Checkout flow" shows aggregation "2 errors"
      And Rule "Cart operations" is connected with tree character "├──"
      And Rule "Checkout flow" is connected with tree character "└──"

    Scenario: failing scenario shows violation codes inline
      Given a feature with a scenario "checkout with valid payment" having violations
      And the violations include missing-placeholder for "price" and missing-literal for "tax"
      When the status command formats the human-readable tree output
      Then the scenario line ends with "price, tax" separated from the title

  Rule: Scenario Statuses Derive from Discovery
    Each scenario receives one of four statuses based on test discovery and consistency
    checking results. The derivation follows a priority-ordered decision tree independent
    of the feature stage computation.

    Scenario: scenario with no matching test function
      Given a ScenarioInfo with function_name "test_delete_item"
      And discover_tests returns no TestInfo for "test_delete_item"
      When the status command computes the scenario status
      Then the status is "no test"
      And is_stub is false
      And violations is an empty tuple

    Scenario: scenario with matching stub test
      Given a ScenarioInfo with function_name "test_create_item"
      And discover_tests returns TestInfo with is_stub True for "test_create_item"
      When the status command computes the scenario status
      Then the status is "no body"
      And is_stub is true
      And violations is an empty tuple

    Scenario: scenario non stub test violations
      Given a ScenarioInfo with function_name "test_update_item" and literals ["new"]
      And discover_tests returns TestInfo with is_stub False and body_constant_nodes []
      And check_pair returns missing-literal violation for "new"
      When the status command computes the scenario status
      Then the status is "1 error"
      And is_stub is false
      And violations count is 1

    Scenario: scenario non stub test zero violations
      Given a ScenarioInfo with function_name "test_list_items" and placeholders ["page"]
      And discover_tests returns TestInfo with is_stub False and body_name_nodes ["page"]
      And check_pair returns empty violations
      When the status command computes the scenario status
      Then the status is "ok"
      And is_stub is false
      And violations is an empty tuple

  Rule: Exit Codes Reflect Overall Status
    The status command exit code must be consistent with beehave check semantics.
    Exit 0 when all features are ok or there are no features.
    Exit 1 when at least one feature is not ok.
    Exit 2 on fatal errors such as missing features directory or disk I/O failure.

    Scenario: all features ok exits zero
      Given a project with 2 feature files
      And feature "login" has stage "ok"
      And feature "signup" has stage "ok"
      When the status command runs
      Then the exit code is 0

    Scenario: any feature not ok exits one
      Given a project with 2 feature files
      And feature "login" has stage "ok"
      And feature "signup" has stage "needs tests"
      When the status command runs
      Then the exit code is 1

    Scenario: broken feature exits with code one
      Given a project with 1 feature file
      And feature "broken_feature" has parse_error_message "No feature found"
      And feature "broken_feature" has stage "broken"
      When the status command runs
      Then the exit code is 1

    Scenario: features directory missing exits two
      Given a project with features_dir set to "nonexistent_dir"
      And the directory "nonexistent_dir" does not exist
      When the status command runs
      Then the exit code is 2
      And an error message is written to stderr

    Scenario: project no feature files exits zero
      Given a project with features directory "docs/features"
      And the directory contains zero .feature files
      When the status command runs
      Then the exit code is 0

  Rule: Orphaned Directories Reported When Flagged
    When --include-orphaned is passed, the status command reports test directories that
    have no matching .feature file. Orphaned directories do not affect any feature stage
    or the exit code.

    Scenario: orphaned directory shown with flag
      Given a test directory "tests/features/removed_feature" exists
      And the test directory contains "default_test.py"
      And no feature file "docs/features/removed_feature.feature" exists
      When the status command runs with --include-orphaned
      Then the StatusReport orphaned_directories contains an entry with path "tests/features/removed_feature"
      And the entry test_files includes "default_test.py"
      And the exit code is not affected by the orphaned directory

    Scenario: orphaned directory not shown without flag
      Given a test directory "tests/features/removed_feature" exists
      And no feature file "docs/features/removed_feature.feature" exists
      When the status command runs without --include-orphaned
      Then the StatusReport orphaned_directories is empty

  Rule: Cross Feature Collisions Detected
    During post-processing across all features, the status command detects test functions
    with the same name appearing in multiple test files. These collisions are reported as
    warnings in the StatusReport but do not affect any feature stage or the exit code.

    Scenario: two features produce same function name
      Given feature "auth" has scenario "login" producing function "test_login"
      And feature "sso" also has scenario "login" producing function "test_login"
      When the status command runs
      Then the StatusReport collisions contains an entry for "test_login"
      And the entry paths includes "tests/features/auth/default_test.py"
      And the entry paths includes "tests/features/sso/default_test.py"
      And the exit code is not affected by the collision

    Scenario: no collisions unique function names
      Given feature "auth" has scenarios producing functions "test_login", "test_logout"
      And feature "payment" has scenarios producing functions "test_charge", "test_refund"
      When the status command runs
      Then the StatusReport collisions is empty

  Rule: JSON Output Is Machine Readable
    When the --json flag is passed, the status command produces a single JSON object with
    features array, orphaned_directories array, collisions array, and summary object.
    The output is valid JSON suitable for consumption by CI systems and dashboards.

    Scenario: JSON output includes full feature hierarchy
      Given a project with 2 feature files
      And feature "auth" has stage "ok" with 3 scenarios all ok
      And feature "payment" has stage "needs fixes" with 2 scenarios
      When the status command runs with --json
      Then the output is valid JSON
      And the JSON has "features" array with 2 entries
      And the JSON has "summary" object with total_features 2
      And the JSON summary.ok is 1
      And the JSON summary.needs_fixes is 1
      And each feature entry has "scenarios" array with scenario detail

    Scenario: JSON includes summary stage counts
      Given a project with 3 feature files
      And features have stages "ok", "broken", "needs bodies"
      When the status command runs with --json
      Then the JSON summary.broken is 1
      And the JSON summary.needs_bodies is 1
      And the JSON summary.ok is 1
      And all other summary counts are 0

    Scenario: JSON has collision and orphan entries
      Given a project with an orphaned directory "tests/features/old_feature"
      And a cross-feature collision on function "test_login"
      When the status command runs with --json and --include-orphaned
      Then the JSON orphaned_directories is not empty
      And the JSON collisions is not empty

  Rule: Test Discovery Failure Yields Needs Tests
    When a test file has a Python syntax error, discover_tests returns an empty dict.
    The status command treats all scenarios in the corresponding feature as unmapped,
    resulting in stage "needs tests". This is a graceful degradation — the feature is
    not marked "broken" because the .feature file itself parsed successfully.

    Scenario: syntax error test file unmaps scenarios
      Given a feature file "docs/features/syntax_error.feature" with 2 scenarios
      And test file "tests/features/syntax_error/default_test.py" has a Python syntax error
      When the status command computes the feature status
      Then discover_tests returns an empty dict
      And all scenario statuses are "no test"
      And the feature stage is "needs tests"
      And scenarios_no_test is 2
      And scenarios_total is 2

    Scenario: empty test file unmaps all scenarios
      Given a feature file "docs/features/empty_test.feature" with 1 scenario
      And test file "tests/features/empty_test/default_test.py" is empty
      When the status command computes the feature status
      Then the feature stage is "needs tests"
      And scenarios_no_test is 1
