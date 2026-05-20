"""Tests for duplicate title detection across feature files."""

from pathlib import Path

from conftest import write_feature

from beehave.config import Config
from beehave.gherkin import validate_all_titles


def test_duplicate_feature_titles(tmp_project: Path, config: Config) -> None:
    """Two feature files with same title (case-insensitive) produce violations."""
    features_root = tmp_project / "docs/features"
    assert features_root.exists()

    feature_file_1 = tmp_project / "docs/features/hive_activity.feature"
    feature_title_1 = "Hive Activity"
    scenario_title_1 = "guard bee inspects visitor"

    write_feature(
        tmp_project,
        "hive_activity",
        f"""\
    Feature: {feature_title_1}

      Scenario: {scenario_title_1}
        Given a guard bee at the hive entrance
        When a visitor bee approaches
        Then the guard bee inspects the visitor
    """,
    )
    assert feature_file_1.exists()

    feature_file_2 = tmp_project / "docs/features/hive_dup.feature"
    feature_title_2 = "hive activity"
    scenario_title_2 = "forager returns with nectar"

    write_feature(
        tmp_project,
        "hive_dup",
        f"""\
    Feature: {feature_title_2}

      Scenario: {scenario_title_2}
        Given a forager bee
        When it returns with nectar
        Then the nectar is deposited in a cell
    """,
    )
    assert feature_file_2.exists()

    result = validate_all_titles(config)
    assert len(result) == 2

    error_types = {v.error_type for v in result}
    assert error_types == {"duplicate-feature-title"}

    paths = {v.path for v in result}
    assert len(paths) == 2
    assert any("hive_activity.feature" in p for p in paths)
    assert any("hive_dup.feature" in p for p in paths)


def test_rule_matches_feature_title(tmp_project: Path, config: Config) -> None:
    """A Rule title matching a Feature title is flagged as duplicate-rule-title."""
    feature_file = tmp_project / "docs/features/rule_v_feature.feature"
    assert feature_file.parent.exists()

    feature_title = "Swarm Detection"
    rule_title = "swarm detection"
    scenario_title = "temperature rise triggers alert"

    write_feature(
        tmp_project,
        "rule_v_feature",
        f"""\
    Feature: {feature_title}

      Rule: {rule_title}

        Scenario: {scenario_title}
          Given a hive temperature sensor
          When the temperature rises above 40 degrees
          Then a swarm alert is triggered
    """,
    )
    assert feature_file.exists()

    result = validate_all_titles(config)
    assert len(result) == 1

    error_types = {v.error_type for v in result}
    assert error_types == {"duplicate-rule-title"}

    paths = {v.path for v in result}
    assert len(paths) == 1
    assert any("rule_v_feature.feature" in p for p in paths)


def test_scenario_matches_feature_title(tmp_project: Path, config: Config) -> None:
    """A Scenario title matching a Feature title is flagged as duplicate-scenario-title."""
    feature_file = tmp_project / "docs/features/scenario_feat.feature"
    assert feature_file.parent.exists()

    feature_title = "Guard Inspection"
    scenario_title = "guard inspection"

    write_feature(
        tmp_project,
        "scenario_feat",
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
    assert len(result) == 1

    error_types = {v.error_type for v in result}
    assert error_types == {"duplicate-scenario-title"}

    paths = {v.path for v in result}
    assert len(paths) == 1
    assert any("scenario_feat.feature" in p for p in paths)


def test_scenario_matches_rule_title(tmp_project: Path, config: Config) -> None:
    """A Scenario title matching a Rule title is flagged as duplicate-scenario-title."""
    feature_file = tmp_project / "docs/features/scenario_rule.feature"
    assert feature_file.parent.exists()

    feature_title = "Hive Activity"
    rule_title = "Foraging Patterns"
    scenario_title = "Foraging Patterns"

    write_feature(
        tmp_project,
        "scenario_rule",
        f"""\
    Feature: {feature_title}

      Rule: {rule_title}

        Scenario: {scenario_title}
          Given a forager bee
          When it returns with pollen
          Then the pollen is deposited
    """,
    )
    assert feature_file.exists()

    result = validate_all_titles(config)
    assert len(result) == 1

    error_types = {v.error_type for v in result}
    assert error_types == {"duplicate-scenario-title"}

    paths = {v.path for v in result}
    assert len(paths) == 1
    assert any("scenario_rule.feature" in p for p in paths)


def test_duplicate_scenarios(tmp_project: Path, config: Config) -> None:
    """Two scenarios in the same file with case-insensitive-equal titles."""
    features_root = tmp_project / "docs/features"
    assert features_root.exists()

    feature_file = tmp_project / "docs/features/dup_scenarios.feature"
    feature_title = "Hive Activity"
    scenario_title_1 = "guard bee inspects visitor"
    scenario_title_2 = "Guard Bee Inspects Visitor"

    write_feature(
        tmp_project,
        "dup_scenarios",
        f"""\
    Feature: {feature_title}

      Scenario: {scenario_title_1}
        Given a guard bee at the hive entrance
        When a visitor bee approaches
        Then the guard bee inspects the visitor

      Scenario: {scenario_title_2}
        Given a guard bee at the hive entrance
        When a visitor bee approaches
        Then the guard bee inspects the visitor
    """,
    )
    assert feature_file.exists()

    result = validate_all_titles(config)
    assert len(result) == 2

    error_types = {v.error_type for v in result}
    assert error_types == {"duplicate-scenario-title"}

    paths = {v.path for v in result}
    assert len(paths) == 1
    assert any("dup_scenarios.feature" in p for p in paths)


def test_mixed_violation_types(tmp_project: Path, config: Config) -> None:
    """One file yields both an invalid-title and a duplicate-title violation."""
    features_root = tmp_project / "docs/features"
    assert features_root.exists()

    mixed_file = tmp_project / "docs/features/mixed.feature"
    mixed_feature_title = "Hive-Activity"
    mixed_rule_title = "Hive Activity"
    mixed_scenario_title = "forager returns with nectar"

    write_feature(
        tmp_project,
        "mixed",
        f"""\
    Feature: {mixed_feature_title}

      Rule: {mixed_rule_title}

        Scenario: {mixed_scenario_title}
          Given a forager bee
          When it returns with nectar
          Then the nectar is deposited
    """,
    )
    assert mixed_file.exists()

    other_file = tmp_project / "docs/features/other.feature"
    other_feature_title = "Hive Activity"
    other_scenario_title = "other scenario"

    write_feature(
        tmp_project,
        "other",
        f"""\
    Feature: {other_feature_title}

      Scenario: {other_scenario_title}
        Given a bee
        When it does something
        Then it happens
    """,
    )
    assert other_file.exists()

    result = validate_all_titles(config)
    assert len(result) == 2

    error_types = {v.error_type for v in result}
    assert error_types == {"invalid-feature-title", "duplicate-rule-title"}

    paths = {v.path for v in result}
    assert len(paths) == 1
    assert any("mixed.feature" in p for p in paths)
