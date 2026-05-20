Feature: Case Insensitive Matching

  Placeholder and literal matching in `beehave check` is case-insensitive.
  `<Dog>` in Gherkin matches `dog`, `DOG`, or `Dog` in the test body.
  `"Rex"` in Gherkin matches `"rex"`, `"Rex"`, or `"REX"` in the test body.
  Literal comparison normalizes both sides via `str().lower()` before
  comparison, preventing type-mismatch false positives. Also fixes four
  bugs in the extraction/comparison pipeline: invisible negative numbers
  (#18), quoted placeholder double-capture (#19), quoted bracket notation
  handling (#20), and type mismatch from `Decimal` values (#22).

  Serves the Consistency Checking bounded context with upstream
  dependencies on Feature Parsing and Test Discovery. Changes are
  localized to `gherkin.py` (literal extraction), `discover.py` (AST
  body node extraction), and `check.py` (comparison logic).

  # Constraints:
  # Technology:
  # - Feature parsing: grep from beehave.gherkin import
  # - Test discovery: grep import ast
  # - Consistency checking: grep from beehave.check import
  # Quality:
  # - Correctness: Case-insensitive comparison is deterministic —
  #   `str().lower()` on both sides always produces the same result.
  # - Reliability: Zero false positives for case variants and type
  #   mismatches resolved by string normalization.
  # - Simplicity: Comparison logic replaces type-based + case-sensitive
  #   checks with a single `str().lower()` normalization pass.

  Background:
    Given a project with features directory "docs/features"
    And a test directory "tests/features/case_insensitive_matching"
    And a feature file "docs/features/case_insensitive_matching.feature"

  Rule: Placeholder Matching Case Insensitive
    When `check_pair()` compares scenario placeholders against test body
    `Name` nodes, it normalizes both sides to lowercase via
    `ph.name.lower()` and `{n.lower() for n in body_name_nodes}`.
    `<Dog>` matches `dog`, `DOG`, and `Dog` in the body. A placeholder
    with a non-matching identifier (e.g., `<Dog>` vs only `cat` in body)
    still produces a `missing-placeholder` violation.

    Scenario: placeholder matches lowercase body name
      Given a scenario step "Given a <Dog> barks"
      And the test body contains identifier "dog"
      When check_pair compares placeholders
      Then zero violations are returned

    Scenario: placeholder matches uppercase body name
      Given a scenario step "Given a <Dog> barks"
      And the test body contains identifier "DOG"
      When check_pair compares placeholders
      Then zero violations are returned

    Scenario: placeholder matches mixed case body name
      Given a scenario step "Given a <Dog> barks"
      And the test body contains identifier "Dog"
      When check_pair compares placeholders
      Then zero violations are returned

    Scenario: placeholder does not match different identifier
      Given a scenario step "Given a <Dog> barks"
      And the test body contains only "cat" and "owner"
      When check_pair compares placeholders
      Then a missing-placeholder violation for "Dog" is returned

  Rule: Literal Matching Case Insensitive
    When `check_pair()` compares scenario literals against test body
    `Constant` nodes, it normalizes both sides via `str(lit.value).lower()`
    and `{str(c).lower() for c in body_constant_nodes}`. String literals
    match regardless of case: `"Rex"` matches `"rex"`, `"Rex"`, `"REX"`.
    Numeric literals are stringified before comparison: `int(77000)` from
    Gherkin matches `str("77000")` from `Decimal("77000")` in the body.

    Scenario: string literal matches lowercase constant
      Given a scenario step 'Given a dog named "Rex"'
      And the test body contains constant "rex"
      When check_pair compares literals
      Then zero violations are returned

    Scenario: string literal matches uppercase constant
      Given a scenario step 'Given a dog named "Rex"'
      And the test body contains constant "REX"
      When check_pair compares literals
      Then zero violations are returned

    Scenario: numeric literal matches stringified decimal
      Given a scenario step "Given the population is 77000"
      And the test body contains constant "77000" from Decimal("77000")
      When check_pair compares literals
      Then zero violations are returned

  Rule: Negative Numbers Visible In Body
    When `discover_tests()` extracts AST body constants, `UnaryOp(USub(),
    Constant(n))` nodes are folded so that both the positive constant `n`
    and the negated value `-n` appear in `body_constant_nodes`. This
    ensures Gherkin literal `-2010` matches `x = -2010` in the test body.

    Scenario: negative integer literal matches body constant
      Given a scenario step "Given the balance is -2010"
      And the test body contains statement "balance = -2010"
      When discover_tests extracts body constants
      Then body_constant_nodes includes -2010
      And check_pair returns zero violations

    Scenario: negative float literal matches body constant
      Given a scenario step "Given the temperature is -3.14"
      And the test body contains statement "temp = -3.14"
      When discover_tests extracts body constants
      Then body_constant_nodes includes -3.14
      And check_pair returns zero violations

    Scenario: positive integer still works
      Given a scenario step "Given the count is 42"
      And the test body contains statement "count = 42"
      When discover_tests extracts body constants
      Then body_constant_nodes includes 42
      And check_pair returns zero violations

  Rule: Quoted Placeholder Not Double Captured
    When `_extract_literals()` processes a quoted string in Gherkin step
    text, any content matching the `<...>` pattern (a valid placeholder
    token) is excluded from literal extraction. The placeholder is
    already captured by `_extract_placeholders()`. This prevents a false
    positive `missing-literal` violation where a literal `<name>` was
    expected in the body but is not a real constant.

    Scenario: quoted placeholder not captured as literal
      Given a step text 'Given a user named "<name>"'
      And "<name>" is a valid placeholder token
      When _extract_literals processes the step text
      Then no Literal is created for "<name>"
      And _extract_placeholders produces Placeholder(name="name")

    Scenario: non-placeholder quoted content still captured
      Given a step text 'Given a phone number "[PHONE]"'
      And "[PHONE]" is not a valid placeholder
      When _extract_literals processes the step text
      Then a Literal with value "[PHONE]" is captured

  Rule: Bracket Notation Preserved As Literal
    When `[...]` appears inside quotes in Gherkin step text, it is
    captured verbatim as a string literal value. Users who want dynamic
    substitution should use `<placeholder>` syntax instead. This is
    intentional behavior — not a bug.

    Scenario: bracket notation captured verbatim
      Given a step text 'Given a phone number "[PHONE]"'
      When literals are extracted from the step text
      Then the literal list contains Literal(value="[PHONE]")

  Rule: True And One Never Collide
    When `check_pair()` normalizes literal values via `str().lower()`,
    `True` produces `"true"` and `1` produces `"1"`. These strings are
    distinct, so Gherkin literal `1` never matches test body constant
    `True`, and vice versa.

    Scenario: integer one does not match boolean true
      Given a scenario step "Given the flag is 1"
      And the test body contains constant True
      When check_pair compares literals
      Then a missing-literal violation for literal 1 is returned

  Rule: Stub Tests Skip All Checks
    When a test body is a stub (containing only `pass` or `...`),
    `check_pair()` returns zero violations regardless of missing
    placeholders or literals. This invariant is unchanged by
    case-insensitive matching.

    Scenario: stub test produces no violations
      Given a scenario step "Given a <Dog> named \"Rex\""
      And the test body is a stub (only "pass")
      When check_pair compares placeholders and literals
      Then zero violations are returned
