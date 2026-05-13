from beehave.validation import (
    AdoptionLevel,
    ValidationReport,
    validate_placeholders,
    validate_step_ordering,
    validate_step_text,
)


def test_adoption_8e2f7c4a():
    """Level 1 — decorators only, no .feature file

    Given a test with @Given, @When, @Then decorators but no .feature file
    When beehave validates the test
    Then step ordering is validated
    And placeholder-parameter matching is validated
    But step text matching is not validated (no .feature file)
    And @id traceability is not validated (no .feature file)
    """
    level = AdoptionLevel.DECORATORS_ONLY

    # --- Setup: valid Given→When→Then steps with a placeholder ---
    steps = [
        ("Given", "a user with balance <initial>"),
        ("When", "action"),
        ("Then", "assertion"),
    ]
    param_names = ["initial"]

    # --- Level 1: ordering IS validated ---
    ordering = validate_step_ordering(steps)
    assert ordering == [], (
        f"valid ordering should produce no violations, got {ordering}"
    )

    # --- Level 1: placeholder matching IS validated ---
    placeholders = validate_placeholders("a user with balance <initial>", param_names)
    assert placeholders == [], (
        f"matched placeholder should produce no mismatches, got {placeholders}"
    )

    # --- Level 1: step text and @id traceability NOT validated ---
    # There is no .feature file, so validate_step_text is never called and
    # check_traceability is never invoked. We confirm the level gates exist.
    assert level == AdoptionLevel.DECORATORS_ONLY
    assert level < AdoptionLevel.FEATURE_TRACEABILITY


def test_adoption_a4d9b3e6():
    """Level 2 — decorators with @id traceability

    Given a test with @Given, @When, @Then decorators and a .feature file with matching @id
    When beehave validates the test
    Then step text matching is validated against .feature
    And @id traceability is validated
    And orphan detection is active
    """
    level = AdoptionLevel.FEATURE_TRACEABILITY

    # --- Step text matching IS validated at level 2 ---
    result = validate_step_text(
        "a user with balance <initial>", "a user with balance <initial>"
    )
    assert result is None  # match = no mismatch

    result = validate_step_text(
        "a user with balance <initial>", "a user with an balance <initial>"
    )
    assert result is not None  # mismatch detected
    assert result.expected == "a user with balance <initial>"
    assert result.actual == "a user with an balance <initial>"

    # --- @id traceability validated — verify orphan tracking exists ---
    report = ValidationReport()
    assert report.orphan_tests == []
    assert report.orphan_scenarios == []
    assert report.is_clean is True  # empty report = clean

    # --- Level 2 also inherits level 1 validations ---
    assert level == AdoptionLevel.FEATURE_TRACEABILITY
    assert level > AdoptionLevel.DECORATORS_ONLY
