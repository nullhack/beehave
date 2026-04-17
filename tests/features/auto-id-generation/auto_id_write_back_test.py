"""Tests for auto id write back story."""

import re
from pathlib import Path

import pytest

from pytest_beehave.id_generator import assign_ids


@pytest.mark.unit
def test_auto_id_generation_cd98877d(tmp_path: Path) -> None:
    """
    Given: a writable .feature file containing an Example with no @id tag
    When: pytest is invoked
    Then: the .feature file contains an @id:<8-char-hex> tag on the line immediately before that Example
    """
    # Given
    feature_file = tmp_path / "in-progress" / "my-feature" / "my-story.feature"
    feature_file.parent.mkdir(parents=True)
    feature_file.write_text(
        "Feature: My feature\n"
        "  Example: Something happens\n"
        "    Given a condition\n"
        "    When an action\n"
        "    Then an outcome\n"
    )
    # When
    assign_ids(tmp_path)
    # Then
    content = feature_file.read_text()
    lines = content.splitlines()
    example_idx = next(i for i, line in enumerate(lines) if "Example:" in line)
    tag_line = lines[example_idx - 1].strip()
    assert re.fullmatch(r"@id:[0-9a-f]{8}", tag_line)


@pytest.mark.unit
@pytest.mark.deprecated
def test_auto_id_generation_09a986e7(tmp_path: Path) -> None:
    """
    Given: a project with multiple .feature files each containing untagged Examples
    When: pytest is invoked
    Then: each generated @id tag is unique across all .feature files in the project
    """
    # Given
    for i in range(3):
        feature_file = tmp_path / "in-progress" / f"feature-{i}" / "story.feature"
        feature_file.parent.mkdir(parents=True)
        feature_file.write_text(
            f"Feature: Feature {i}\n"
            f"  Example: Example {i} A\n"
            f"    Given a condition\n"
            f"    When an action\n"
            f"    Then an outcome\n"
            f"  Example: Example {i} B\n"
            f"    Given another condition\n"
            f"    When another action\n"
            f"    Then another outcome\n"
        )
    # When
    assign_ids(tmp_path)
    # Then
    id_pattern = re.compile(r"@id:([0-9a-f]{8})")
    found_ids: list[str] = []
    for feature_file in tmp_path.rglob("*.feature"):
        found_ids.extend(id_pattern.findall(feature_file.read_text()))
    assert len(found_ids) == len(set(found_ids))


@pytest.mark.unit
def test_auto_id_generation_27cf14bf(tmp_path: Path) -> None:
    """
    Given: a writable .feature file containing multiple untagged Examples
    When: pytest is invoked
    Then: all generated @id tags within that file are unique
    """
    # Given
    feature_file = tmp_path / "in-progress" / "my-feature" / "my-story.feature"
    feature_file.parent.mkdir(parents=True)
    feature_file.write_text(
        "Feature: My feature\n"
        "  Example: First example\n"
        "    Given a condition\n"
        "    When an action\n"
        "    Then an outcome\n"
        "  Example: Second example\n"
        "    Given another condition\n"
        "    When another action\n"
        "    Then another outcome\n"
        "  Example: Third example\n"
        "    Given yet another condition\n"
        "    When yet another action\n"
        "    Then yet another outcome\n"
    )
    # When
    assign_ids(tmp_path)
    # Then
    content = feature_file.read_text()
    found_ids = re.findall(r"@id:([0-9a-f]{8})", content)
    assert len(found_ids) == 3
    assert len(found_ids) == len(set(found_ids))


@pytest.mark.unit
def test_auto_id_generation_842409ed(tmp_path: Path) -> None:
    """
    Given: a .feature file where all Examples already have @id tags
    When: pytest is invoked
    Then: the .feature file content is unchanged
    """
    # Given
    original_content = (
        "Feature: My feature\n"
        "  @id:aabbccdd\n"
        "  Example: Something happens\n"
        "    Given a condition\n"
        "    When an action\n"
        "    Then an outcome\n"
    )
    feature_file = tmp_path / "in-progress" / "my-feature" / "my-story.feature"
    feature_file.parent.mkdir(parents=True)
    feature_file.write_text(original_content)
    # When
    assign_ids(tmp_path)
    # Then
    assert feature_file.read_text() == original_content
