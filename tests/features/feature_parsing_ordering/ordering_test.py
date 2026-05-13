from beehave.validation import validate_step_ordering


def test_ordering_9f5d3b2a():
    """Valid step ordering passes validation

    Given a test with decorators @Given, @When, @Then in order
    When beehave validates step ordering
    Then no ordering violation is reported
    """
    steps = [("Given", "setup"), ("When", "action"), ("Then", "assertion")]
    violations = validate_step_ordering(steps)
    assert violations == []


def test_ordering_1c8e4a7d():
    """Invalid step ordering fails validation

    Given a test with decorators @Then, @Given, @When (out of order)
    When beehave validates step ordering
    Then an ordering violation is reported
    """
    steps = [("Then", "assertion"), ("Given", "setup"), ("When", "action")]
    violations = validate_step_ordering(steps)
    assert len(violations) >= 1
    assert violations[0].step_index == 1
    assert violations[0].actual_keyword == "Given"


def test_ordering_b7e2f1a4():
    """@And/@But inherit preceding step type for ordering

    Given a test with decorators @Given, @And, @When, @And, @Then, @But in order
    When beehave validates step ordering
    Then no ordering violation is reported
    """
    steps = [
        ("Given", "setup"),
        ("And", "more setup"),
        ("When", "action"),
        ("And", "more action"),
        ("Then", "assertion"),
        ("But", "negative assertion"),
    ]
    violations = validate_step_ordering(steps)
    assert violations == []


def test_ordering_and_before_given():
    """And/But before any defining keyword reports violation

    Given a test with @And as the first step (no preceding Given/When/Then)
    When beehave validates step ordering
    Then an ordering violation is reported with appropriate message
    """
    steps = [("And", "setup")]
    violations = validate_step_ordering(steps)
    assert len(violations) == 1
    assert violations[0].step_index == 0
    assert violations[0].actual_keyword == "And"
    assert "Given/When/Then must precede And/But" in violations[0].expected_after


def test_ordering_when_after_then():
    """When after Then reports violation with correct expected_after

    Given a test with @Then followed by @When (out of order)
    When beehave validates step ordering
    Then an ordering violation is reported with 'Given' in expected_after
    """
    steps = [("Then", "check"), ("When", "act")]
    violations = validate_step_ordering(steps)
    assert len(violations) == 1
    assert violations[0].step_index == 1
    assert violations[0].actual_keyword == "When"
    assert "Given" in violations[0].expected_after
