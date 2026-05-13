"""Test stubs for generate_messaging feature.

Generated from: docs/features/generate_messaging.feature
Rule: Advisory for scenarios without @id tags
Rule: Empty feature file produces distinct message
"""

from beehave.cli import generate


def test_generate_messaging_7a3f9b2e(tmp_path, monkeypatch) -> None:
    """All scenarios lack @id tags — advisory message with count, no stubs created.

    Given a .feature file containing 3 scenarios, none with @id tags
    When the developer runs `beehave generate` for that feature
    Then the output contains "3 scenarios found without @id tags"
    And the output contains "Run 'beehave sync' first"
    And no test stubs are created
    And no .feature files are modified
    """
    features_dir = tmp_path / "docs" / "features"
    features_dir.mkdir(parents=True)
    feature_content = (
        "Feature: Untagged Feature\n"
        "  Rule: R1\n"
        "    Example: First scenario\n"
        "      Given something\n"
        "    Example: Second scenario\n"
        "      Given something else\n"
        "    Example: Third scenario\n"
        "      Given another thing\n"
    )
    feature_file = features_dir / "untagged.feature"
    original_content = feature_content
    feature_file.write_text(feature_content)

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("beehave.cli._is_interactive", lambda: False)

    output = generate("untagged", json_output=False)
    assert output is not None
    assert "3 scenarios found without @id tags" in output
    assert "Run 'beehave sync' first" in output

    # No test stubs created
    test_dir = tmp_path / "tests" / "features" / "untagged"
    assert not test_dir.exists()

    # No .feature files modified
    assert feature_file.read_text() == original_content


def test_generate_messaging_8c4d0e6f(tmp_path, monkeypatch) -> None:
    """Some scenarios lack @id tags — stubs for tagged ones, warning about untagged count.

    Given a .feature file containing 5 scenarios where 3 have @id tags and 2 do not
    When the developer runs `beehave generate` for that feature
    Then test stubs are created for the 3 tagged scenarios
    And the output contains "2 scenarios found without @id tags"
    And the output contains "Run 'beehave sync' first"
    And no .feature files are modified
    """
    features_dir = tmp_path / "docs" / "features"
    features_dir.mkdir(parents=True)
    feature_content = (
        "Feature: Mixed Tagging\n"
        "  Rule: R1\n"
        "    @id:aa110000\n"
        "    Example: Tagged first\n"
        "      Given something\n"
        "    Example: Untagged first\n"
        "      Given something\n"
        "    @id:bb220000\n"
        "    Example: Tagged second\n"
        "      Given something\n"
        "    Example: Untagged second\n"
        "      Given something\n"
        "    @id:cc330000\n"
        "    Example: Tagged third\n"
        "      Given something\n"
    )
    feature_file = features_dir / "mixed_tagging.feature"
    original_content = feature_content
    feature_file.write_text(feature_content)

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("beehave.cli._is_interactive", lambda: False)

    output = generate("mixed_tagging", json_output=False)
    assert output is not None
    assert "2 scenarios found without @id tags" in output
    assert "Run 'beehave sync' first" in output

    # Test stubs created for the 3 tagged scenarios
    test_dir = tmp_path / "tests" / "features" / "mixed_tagging"
    test_file = test_dir / "default_test.py"
    assert test_file.exists()
    stub_content = test_file.read_text()
    assert "aa110000" in stub_content
    assert "bb220000" in stub_content
    assert "cc330000" in stub_content

    # No .feature files modified
    assert feature_file.read_text() == original_content


def test_generate_messaging_2b5e1a9c(tmp_path, monkeypatch) -> None:
    """Feature file with zero scenarios — distinct "no scenarios found" message.

    Given a .feature file containing 0 scenarios
    When the developer runs `beehave generate` for that feature
    Then the output contains "no scenarios found"
    And the output does NOT contain "without @id tags"
    And no test stubs are created
    """
    features_dir = tmp_path / "docs" / "features"
    features_dir.mkdir(parents=True)
    (features_dir / "empty.feature").write_text(
        "Feature: Empty\n  Rule: Nothing here\n"
    )

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("beehave.cli._is_interactive", lambda: False)

    output = generate("empty", json_output=False)
    assert output is not None
    assert "no scenarios found" in output
    assert "without @id tags" not in output

    # No test stubs created
    test_dir = tmp_path / "tests" / "features" / "empty"
    assert not test_dir.exists()
