"""Test stubs for scenario_outline_idempotency feature.

Generated from: docs/features/scenario_outline_idempotency.feature
Rule: Expanded row @ids are deterministic across parses
Rule: Generate is idempotent for Scenario Outline
"""

from beehave.cli import generate
from beehave.traceability import parse_feature


def test_scenario_outline_idempotency_d70b43c7() -> None:
    """Same Examples rows produce same @ids across two parses.

    Given a .feature file with "Scenario Outline: parameterized" and 3 Examples rows
    When parse_feature() is called twice
    Then the @ids of all expanded rows are identical between both parses
    """
    feature_text = (
        "Feature: test\n"
        "  @id:abcdef01\n"
        "  Scenario Outline: parameterized\n"
        "    Given a value <value>\n"
        "    Examples:\n"
        "      | value |\n"
        "      | 1 |\n"
        "      | 2 |\n"
        "      | 3 |\n"
    )
    scenarios1 = parse_feature(feature_text)
    scenarios2 = parse_feature(feature_text)
    ids1 = [s.id_tag.value for s in scenarios1]
    ids2 = [s.id_tag.value for s in scenarios2]
    assert ids1 == ids2


def test_scenario_outline_idempotency_6bf99005() -> None:
    """Different row indices produce different @ids.

    Given a .feature file with "Scenario Outline: test" and 2 Examples rows
    When parse_feature() expands the rows
    Then row 0 and row 1 have different @id tags
    """
    feature_text = (
        "Feature: test\n"
        "  @id:abcdef01\n"
        "  Scenario Outline: test\n"
        "    Given a value <value>\n"
        "    Examples:\n"
        "      | value |\n"
        "      | 1 |\n"
        "      | 2 |\n"
    )
    scenarios = parse_feature(feature_text)
    assert len(scenarios) == 2
    assert scenarios[0].id_tag.value != scenarios[1].id_tag.value


def test_scenario_outline_idempotency_af9221cf(tmp_path, monkeypatch) -> None:
    """Running generate twice appends no duplicates.

    Given a .feature file with "Scenario Outline: values" and 2 Examples rows
    And beehave generate has been run once, producing 2 test functions
    When beehave generate is run a second time
    Then no new test functions are appended
    And the test file still contains exactly 2 test functions
    """
    feature_text = (
        "Feature: test outline\n"
        "  @id:abcdef01\n"
        "  Scenario Outline: values\n"
        "    Given a value <value>\n"
        "    Examples:\n"
        "      | value |\n"
        "      | 1 |\n"
        "      | 2 |\n"
    )
    feature_dir = tmp_path / "docs" / "features"
    feature_dir.mkdir(parents=True)
    feature_file = feature_dir / "test_outline.feature"
    feature_file.write_text(feature_text)

    test_dir = tmp_path / "tests" / "features" / "test_outline"
    test_dir.mkdir(parents=True)

    monkeypatch.chdir(tmp_path)

    # First generate
    generate("test_outline")
    test_file = test_dir / "default_test.py"
    assert test_file.exists()
    content1 = test_file.read_text()
    count1 = content1.count("def test_")

    # Second generate
    generate("test_outline")
    content2 = test_file.read_text()
    count2 = content2.count("def test_")

    assert count1 == 2
    assert count2 == 2


def test_scenario_outline_idempotency_146758c7(tmp_path, monkeypatch) -> None:
    """Running generate multiple times is idempotent.

    Given a .feature file with Scenario Outline and Examples
    When beehave generate is run 3 times consecutively
    Then the test file contains exactly one test function per Examples row
    """
    feature_text = (
        "Feature: multi outline\n"
        "  @id:abcdef01\n"
        "  Scenario Outline: values\n"
        "    Given a value <value>\n"
        "    Examples:\n"
        "      | value |\n"
        "      | 1 |\n"
        "      | 2 |\n"
        "      | 3 |\n"
    )
    feature_dir = tmp_path / "docs" / "features"
    feature_dir.mkdir(parents=True)
    feature_file = feature_dir / "multi_outline.feature"
    feature_file.write_text(feature_text)

    test_dir = tmp_path / "tests" / "features" / "multi_outline"
    test_dir.mkdir(parents=True)

    monkeypatch.chdir(tmp_path)

    for _ in range(3):
        generate("multi_outline")

    test_file = test_dir / "default_test.py"
    content = test_file.read_text()
    count = content.count("def test_")
    assert count == 3
