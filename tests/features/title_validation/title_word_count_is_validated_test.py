"""Tests for title word-count validation (2-6 words)."""

from pathlib import Path

import pytest
from conftest import write_feature

from beehave.config import Config
from beehave.gherkin import validate_all_titles


def test_feature_title_has_one_word(tmp_project: Path, config: Config) -> None:
    """A one-word Feature title is flagged as invalid-feature-title."""
    features_root = tmp_project / "docs/features"
    assert features_root.exists()

    feature_file = tmp_project / "docs/features/single_word.feature"
    feature_title = "Activity"

    write_feature(
        tmp_project,
        "single_word",
        f"""\
    Feature: {feature_title}

      Scenario: simple scenario
        Given a bee
        When it flies
        Then it lands
    """,
    )
    assert feature_file.exists()

    result = validate_all_titles(config)
    assert len(result) == 1
    violation = result[0]
    assert violation.error_type == "invalid-feature-title"
    assert "word" in violation.message.lower()


def test_seven_word_title(tmp_project: Path, config: Config) -> None:
    """A seven-word Feature title is flagged as invalid-feature-title."""
    features_root = tmp_project / "docs/features"
    assert features_root.exists()

    feature_file = tmp_project / "docs/features/seven_word_title.feature"
    feature_title = "My Seven Word Feature Title Is Here"

    write_feature(
        tmp_project,
        "seven_word_title",
        f"""\
    Feature: {feature_title}

      Scenario: simple scenario
        Given a bee
        When it flies
        Then it lands
    """,
    )
    assert feature_file.exists()

    result = validate_all_titles(config)
    assert len(result) == 1
    violation = result[0]
    assert violation.error_type == "invalid-feature-title"
    assert "word" in violation.message.lower()


@pytest.mark.skip(reason="not implemented")
def test_rule_title_has_seven_words() -> None:
    """Rule title with seven words."""
    ...


@pytest.mark.skip(reason="not implemented")
def test_scenario_title_is_empty_string() -> None:
    """Scenario title consisting of an empty string."""
    ...


def test_empty_title_after_strip(tmp_project: Path, config: Config) -> None:
    """A whitespace-only title is equivalent to empty and is flagged."""
    features_root = tmp_project / "docs/features"
    assert features_root.exists()

    feature_file = tmp_project / "docs/features/whitespace_title.feature"
    feature_title = "   "

    write_feature(
        tmp_project,
        "whitespace_title",
        f"""\
    Feature: {feature_title}

      Scenario: simple scenario
        Given a bee
        When it flies
        Then it lands
    """,
    )
    assert feature_file.exists()

    result = validate_all_titles(config)
    assert len(result) == 1
    violation = result[0]
    assert violation.error_type == "invalid-feature-title"
    assert "non-empty" in violation.message.lower()
