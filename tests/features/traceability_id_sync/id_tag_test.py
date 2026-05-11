from beehave.traceability import (
    OrphanScenario,
    OrphanTest,
    check_traceability,
    generate_id,
    parse_feature,
)


def test_id_tag_c7f2a8d5() -> None:
    """beehave sync generates an 8-character random ID for scenarios without one.

    Given a .feature scenario without an @id tag
    When the developer runs beehave sync
    Then beehave generates an 8-character random ID and writes @id:<id> into the .feature file
    """
    id_value = generate_id()
    assert len(id_value) == 8
    assert all(c in "0123456789abcdef" for c in id_value)


def test_id_tag_a1f4e8b7() -> None:
    """@id tags remain unchanged when scenario text is edited.

    Given a .feature scenario with @id:c7f2a8d5
    When the developer edits the scenario text
    Then the @id tag remains unchanged
    """
    feature_text = (
        "Feature: Test\n"
        "  Rule: Example rule\n"
        "    @id:c7f2a8d5\n"
        "    Example: original name\n"
        "      Given something\n"
    )
    edited_text = feature_text.replace("original name", "edited name")
    scenarios_before = parse_feature(feature_text)
    scenarios_after = parse_feature(edited_text)
    assert scenarios_after[0].id_tag == "c7f2a8d5"
    assert scenarios_before[0].id_tag == scenarios_after[0].id_tag


def test_id_tag_6d4f8a2e() -> None:
    """Scenarios with @id tags but no matching test function are reported as orphans.

    Given a .feature scenario with @id:m3n4o5p6 that has no matching test function
    When the developer runs beehave sync
    Then the scenario is reported as an orphan scenario
    """
    result = check_traceability(
        feature_ids=["m3n4o5p6"],
        test_ids=[],
    )
    assert len(result.orphan_scenarios) == 1
    assert isinstance(result.orphan_scenarios[0], OrphanScenario)
    assert result.orphan_scenarios[0].id_tag == "m3n4o5p6"


def test_id_tag_f1c7d5b9() -> None:
    """Test functions with @id suffixes that have no matching .feature scenario are reported as orphans.

    Given a test function with @id suffix that has no matching .feature scenario
    When the developer runs beehave sync
    Then the test is reported as an orphan test
    """
    result = check_traceability(
        feature_ids=[],
        test_ids=["abc12345"],
    )
    assert len(result.orphan_tests) == 1
    assert isinstance(result.orphan_tests[0], OrphanTest)
    assert result.orphan_tests[0].id_tag == "abc12345"
