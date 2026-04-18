"""Tests for auto id generation — auto ID write-back rule."""

import re
from pathlib import Path

from pytest_beehave.id_generator import assign_ids


def _make_feature_file(directory: Path, content: str) -> Path:
    """Write a feature file under directory and return its path."""
    path = directory / "in-progress" / "my-feature" / "my-story.feature"
    path.parent.mkdir(parents=True)
    path.write_text(content)
    return path


def _single_example_content() -> str:
    """Return feature file text with one untagged Example."""
    return (
        "Feature: My feature\n"
        "  Example: Something happens\n"
        "    Given a condition\n"
        "    When an action\n"
        "    Then an outcome\n"
    )


def _three_examples_content() -> str:
    """Return feature file text with three untagged Examples."""
    return (
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


class TestAutoIdWriteBack:
    """Tests for the Auto ID write-back Rule."""

    def test_auto_id_write_back_cd98877d(self, tmp_path: Path) -> None:
        """
        Given: a writable .feature file containing an Example with no @id tag
        When: pytest is invoked
        Then: the .feature file contains an @id:<8-char-hex> tag on the line immediately before that Example
        """
        feature_file = _make_feature_file(tmp_path, _single_example_content())
        assign_ids(tmp_path)
        lines = feature_file.read_text().splitlines()
        example_idx = next(i for i, line in enumerate(lines) if "Example:" in line)
        assert re.fullmatch(r"@id:[0-9a-f]{8}", lines[example_idx - 1].strip())

    def test_auto_id_write_back_27cf14bf(self, tmp_path: Path) -> None:
        """
        Given: a writable .feature file containing multiple untagged Examples
        When: pytest is invoked
        Then: all generated @id tags within that file are unique
        """
        feature_file = _make_feature_file(tmp_path, _three_examples_content())
        assign_ids(tmp_path)
        found_ids = re.findall(r"@id:([0-9a-f]{8})", feature_file.read_text())
        assert len(found_ids) == 3
        assert len(found_ids) == len(set(found_ids))

    def test_auto_id_write_back_842409ed(self, tmp_path: Path) -> None:
        """
        Given: a .feature file where all Examples already have @id tags
        When: pytest is invoked
        Then: the .feature file content is unchanged
        """
        original_content = (
            "Feature: My feature\n"
            "  @id:aabbccdd\n"
            "  Example: Something happens\n"
            "    Given a condition\n"
            "    When an action\n"
            "    Then an outcome\n"
        )
        feature_file = _make_feature_file(tmp_path, original_content)
        assign_ids(tmp_path)
        assert feature_file.read_text() == original_content
