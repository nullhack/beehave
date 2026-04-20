"""Tests for auto id generation — auto ID write-back rule."""

import re
from pathlib import Path

import pytest

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


def test_auto_id_generation_a7b5c493(tmp_path: Path) -> None:
    """
    Given: a writable .feature file containing an Example tagged @id:my-custom-name (non-hex format)
    When: pytest is invoked
    Then: the generated stub function is named test_<feature_slug>_my-custom-name and no additional @id tag is written to the .feature file
    """
    from pytest_beehave.sync_engine import run_sync

    features_dir = tmp_path / "features"
    tests_dir = tmp_path / "tests" / "features"
    feature_path = features_dir / "in-progress" / "my-feature" / "my-story.feature"
    feature_path.parent.mkdir(parents=True)
    feature_path.write_text(
        "Feature: My feature\n"
        "  Rule: My rule\n"
        "    @id:my-custom-name\n"
        "    Example: Something happens\n"
        "      Given a condition\n"
        "      When an action\n"
        "      Then an outcome\n"
    )
    assign_ids(features_dir)
    content_after_id = feature_path.read_text()
    run_sync(features_dir, tests_dir)
    test_file = tests_dir / "my_feature" / "my_rule_test.py"
    stub_content = test_file.read_text()
    assert content_after_id.count("@id:") == 1
    assert "test_my_feature_my-custom-name" in stub_content


@pytest.mark.skip(reason="not yet implemented")
def test_auto_id_generation_b8c6d504() -> None:
    """
    Given: a .feature file containing an Example with two @id tags on separate lines before the Example keyword
    When: pytest is invoked
    Then: pytest exits with a non-zero status code and an error message naming the Example with duplicate @id tags
    """
    raise NotImplementedError

