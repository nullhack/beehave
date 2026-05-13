import re

from beehave.cli import _generate_stub_content, _to_snake_case


def test_traceability_generate_core_3e9b1c6a() -> None:
    """Test function name includes @id suffix after snake_case conversion of scenario title.

    Given a .feature scenario with @id:kx7m2p9q
    When beehave generate creates a test function for this scenario
    Then the generated test function is named test_<scenario_title_snake_case>_kx7m2p9q
    And the snake_case portion is NFKD-normalized, truncated to 80 characters, and the @id suffix is always included in full
    """
    content = _generate_stub_content(
        scenario_name="Some scenario title",
        scenario_id="kx7m2p9q",
        steps=["Given something"],
        examples=[],
    )
    assert "def test_some_scenario_title_kx7m2p9q" in content

    # Truncation: snake_case portion is at most 80 chars, @id always included in full
    long_title = "Word " * 100
    content_long = _generate_stub_content(
        scenario_name=long_title,
        scenario_id="kx7m2p9q",
        steps=[],
        examples=[],
    )
    func_match = re.search(r"def (test_\w+)", content_long)
    assert func_match
    func_name = func_match.group(1)
    assert func_name.endswith("_kx7m2p9q")
    snake_part = func_name[5 : -len("_kx7m2p9q")]
    assert len(snake_part) <= 80


def test_traceability_generate_core_d6f8a2c4() -> None:
    """Snake_case conversion handles special characters in scenario titles.

    Given a .feature scenario titled "Ünïcödé: a café's 3 attempts"
    When beehave generate creates a test function
    Then the function name starts with "unicode_a_cafe_s_scenario_3_attempts_" followed by the @id
    """
    result = _to_snake_case("Ünïcödé: a café's 3 attempts")
    assert result == "unicode_a_cafe_s_scenario_3_attempts"
