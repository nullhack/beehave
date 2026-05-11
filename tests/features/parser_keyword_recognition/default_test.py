from beehave.traceability import parse_feature


def test_parser_keyword_recognition_7f3a9c2e() -> None:
    """Scenario Outline is recognized as a scenario heading.

    Given a .feature file containing "Scenario Outline: parameterized login"
    When the parser processes the file
    Then "parameterized login" appears in the parsed scenario list
    """
    feature_text = (
        "Feature: Login\n"
        "  @id:aaa\n"
        "  Scenario Outline: parameterized login\n"
        "    Given a user <name>\n"
    )
    scenarios = parse_feature(feature_text)
    names = [s.name.value for s in scenarios]
    assert "parameterized login" in names


def test_parser_keyword_recognition_b4e18d6f() -> None:
    """Scenario Template is recognized as a scenario heading.

    Given a .feature file containing "Scenario Template: data-driven withdrawal"
    When the parser processes the file
    Then "data-driven withdrawal" appears in the parsed scenario list
    """
    feature_text = (
        "Feature: Withdrawal\n"
        "  @id:bbb\n"
        "  Scenario Template: data-driven withdrawal\n"
        "    Given an account with balance <amount>\n"
    )
    scenarios = parse_feature(feature_text)
    names = [s.name.value for s in scenarios]
    assert "data-driven withdrawal" in names


def test_parser_keyword_recognition_2c8f5a1d() -> None:
    """Two Examples rows produce two separate scenarios with distinct @id tags.

    Given a .feature file with "Scenario Outline: parameterized login" and an Examples table with 2 rows
    When the parser expands the scenario outline
    Then 2 separate Scenario entities are produced
    And each has a distinct @id tag
    """
    feature_text = (
        "Feature: Login\n"
        "  @id:aaa\n"
        "  Scenario Outline: parameterized login\n"
        "    Given a user <name>\n"
        "    Examples:\n"
        "      | name  |\n"
        "      | Alice |\n"
        "      | Bob   |\n"
    )
    scenarios = parse_feature(feature_text)
    assert len(scenarios) == 2
    id_tags = [s.id_tag for s in scenarios if s.id_tag is not None]
    assert len(set(str(t) for t in id_tags)) == 2


def test_parser_keyword_recognition_9e6b3f7a() -> None:
    """A single-row Examples table produces one scenario with its own @id.

    Given a .feature file with "Scenario Outline: edge case" and an Examples table with 1 row
    When the parser expands the scenario outline
    Then 1 Scenario entity is produced with its own @id tag
    """
    feature_text = (
        "Feature: Edge\n"
        "  @id:ccc\n"
        "  Scenario Outline: edge case\n"
        "    Given a boundary value <val>\n"
        "    Examples:\n"
        "      | val |\n"
        "      | 0   |\n"
    )
    scenarios = parse_feature(feature_text)
    assert len(scenarios) == 1
    assert scenarios[0].id_tag is not None


def test_parser_keyword_recognition_d1a4c8e2() -> None:
    """Steps from a regular Scenario do not leak into an adjacent Scenario Outline.

    Given a .feature file with "Scenario: first" followed by "Scenario Outline: second"
    And "Scenario: first" has Given/When/Then steps "setup first", "action first", "result first"
    And "Scenario Outline: second" has Given/When/Then steps "setup second", "action second", "result second"
    When the parser processes both scenarios
    Then "Scenario: first" contains only "setup first", "action first", "result first"
    And "Scenario Outline: second" contains only "setup second", "action second", "result second"
    """
    from beehave.cli import _parse_feature_steps

    feature_text = (
        "Feature: Leakage Test\n"
        "  @id:aaa11111\n"
        "  Scenario: first\n"
        "    Given setup first\n"
        "    When action first\n"
        "    Then result first\n"
        "  @id:bbb22222\n"
        "  Scenario Outline: second\n"
        "    Given setup second\n"
        "    When action second\n"
        "    Then result second\n"
        "    Examples:\n"
        "      | x |\n"
        "      | 1 |\n"
    )
    scenarios = parse_feature(feature_text)
    # Both scenarios must be recognized
    assert len(scenarios) == 2

    name_to_id = {s.name.value: str(s.id_tag) for s in scenarios if s.id_tag}
    steps_map = _parse_feature_steps(feature_text)

    first_steps = [text for _, text in steps_map.get(name_to_id["first"], [])]
    second_steps = [text for _, text in steps_map.get(name_to_id["second"], [])]

    assert first_steps == ["setup first", "action first", "result first"]
    assert second_steps == ["setup second", "action second", "result second"]


def test_parser_keyword_recognition_5f2d7b9c() -> None:
    """Steps from a Scenario Outline do not leak into an adjacent regular Scenario.

    Given a .feature file with "Scenario Outline: parameterized" followed by "Scenario: standalone"
    And "Scenario Outline: parameterized" has Given/When/Then steps "param setup", "param action", "param result"
    And "Scenario: standalone" has Given/When/Then steps "solo setup", "solo action", "solo result"
    When the parser processes both scenarios
    Then "Scenario Outline: parameterized" contains only "param setup", "param action", "param result"
    And "Scenario: standalone" contains only "solo setup", "solo action", "solo result"
    """
    from beehave.cli import _parse_feature_steps

    feature_text = (
        "Feature: Reverse Leakage Test\n"
        "  @id:ccc33333\n"
        "  Scenario Outline: parameterized\n"
        "    Given param setup\n"
        "    When param action\n"
        "    Then param result\n"
        "    Examples:\n"
        "      | y |\n"
        "      | 2 |\n"
        "  @id:ddd44444\n"
        "  Scenario: standalone\n"
        "    Given solo setup\n"
        "    When solo action\n"
        "    Then solo result\n"
    )
    scenarios = parse_feature(feature_text)
    # Both scenarios must be recognized
    assert len(scenarios) == 2

    name_to_id = {s.name.value: str(s.id_tag) for s in scenarios if s.id_tag}
    steps_map = _parse_feature_steps(feature_text)

    param_steps = [text for _, text in steps_map.get(name_to_id["parameterized"], [])]
    solo_steps = [text for _, text in steps_map.get(name_to_id["standalone"], [])]

    assert param_steps == ["param setup", "param action", "param result"]
    assert solo_steps == ["solo setup", "solo action", "solo result"]
