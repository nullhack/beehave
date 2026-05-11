from beehave.validation import Mismatch, validate_step_text


def test_feature_parsing_mapping_4c1f8d3b():
    """Exact step text match passes validation

    Given a .feature step "Given a user with balance <initial>"
    And a test decorator @Given("a user with balance <initial>")
    When beehave validates the step
    Then no mismatch is reported
    """
    result = validate_step_text(
        "a user with balance <initial>",
        "a user with balance <initial>",
    )
    assert result is None


def test_feature_parsing_mapping_e6a2c7f9():
    """Step text mismatch fails validation

    Given a .feature step "Given a user with balance <initial>"
    And a test decorator @Given("a user with an balance <initial>")
    When beehave validates the step
    Then a mismatch is reported showing expected "a user with balance <initial>" and actual "a user with an balance <initial>"
    """
    result = validate_step_text(
        "a user with balance <initial>",
        "a user with an balance <initial>",
    )
    assert isinstance(result, Mismatch)
    assert result.expected == "a user with balance <initial>"
    assert result.actual == "a user with an balance <initial>"
