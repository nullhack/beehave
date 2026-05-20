"""Tests that valid titles produce no violations."""

from pathlib import Path

import pytest
from conftest import write_feature

from beehave.config import Config
from beehave.gherkin import validate_all_titles


def test_single_valid_file(tmp_project: Path, config: Config) -> None:
    """A single file with valid unique titles produces an empty violations list."""
    features_root = tmp_project / "docs/features"
    assert features_root.exists()

    feature_file = tmp_project / "docs/features/hive_activity.feature"
    feature_title = "Hive Activity"
    rule_title = "Hive defense"
    scenario_title = "guard bee inspects visitor"

    write_feature(
        tmp_project,
        "hive_activity",
        f"""\
    Feature: {feature_title}

      Rule: {rule_title}
        Scenario: {scenario_title}
          Given a guard bee at the hive entrance
          When a visitor bee approaches
          Then the guard bee inspects the visitor
    """,
    )
    assert feature_file.exists()

    result = validate_all_titles(config)
    assert result == []


def test_two_files_with_valid_unique_titles(tmp_project: Path, config: Config) -> None:
    """Two files with distinct valid titles produce no violations."""
    features_root = tmp_project / "docs/features"
    assert features_root.exists()

    feature_file_1 = tmp_project / "docs/features/hive_activity.feature"
    feature_title_1 = "Hive Activity"
    rule_title_1 = "Hive defense"
    scenario_title_1 = "guard bee inspects visitor"

    write_feature(
        tmp_project,
        "hive_activity",
        f"""\
    Feature: {feature_title_1}

      Rule: {rule_title_1}
        Scenario: {scenario_title_1}
          Given a guard bee at the hive entrance
          When a visitor bee approaches
          Then the guard bee inspects the visitor
    """,
    )
    assert feature_file_1.exists()

    feature_file_2 = tmp_project / "docs/features/comb_construction.feature"
    feature_title_2 = "Comb Construction"
    rule_title_2 = "Wax Production"
    scenario_title_2 = "worker builds hexagonal cells"

    write_feature(
        tmp_project,
        "comb_construction",
        f"""\
    Feature: {feature_title_2}

      Rule: {rule_title_2}
        Scenario: {scenario_title_2}
          Given a worker bee
          When it builds a cell
          Then the cell is hexagonal
    """,
    )
    assert feature_file_2.exists()

    result = validate_all_titles(config)
    assert result == []


def test_minimum_word_count_title(tmp_project: Path, config: Config) -> None:
    """A two-word title (minimum allowed) produces no violations."""
    features_root = tmp_project / "docs/features"
    assert features_root.exists()

    feature_file = tmp_project / "docs/features/minimal.feature"
    feature_title = "Minimal Title"
    scenario_title = "simple test"

    write_feature(
        tmp_project,
        "minimal",
        f"""\
    Feature: {feature_title}

      Scenario: {scenario_title}
        Given a guard bee at the hive entrance
        When a visitor bee approaches
        Then the guard bee inspects the visitor
    """,
    )
    assert feature_file.exists()

    result = validate_all_titles(config)
    assert result == []


@pytest.mark.skip(reason="not implemented")
def test_maximum_word_count_title() -> None:
    """A title with exactly six words passes validation."""
    ...
