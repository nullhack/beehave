"""Tests for title character-set validation."""

from pathlib import Path

from conftest import write_feature

from beehave.config import Config
from beehave.gherkin import validate_all_titles


def test_feature_title_with_hyphen(tmp_project: Path, config: Config) -> None:
    """A Feature title containing a hyphen is flagged as invalid-feature-title."""
    features_root = tmp_project / "docs/features"
    assert features_root.exists()

    feature_file = tmp_project / "docs/features/bad_title.feature"
    feature_title = "Hive-Activity"

    write_feature(
        tmp_project,
        "bad_title",
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
    assert "invalid" in violation.message.lower()


def test_rule_title_with_period(tmp_project: Path, config: Config) -> None:
    """A Rule title containing a period is flagged as invalid-rule-title."""
    features_root = tmp_project / "docs/features"
    assert features_root.exists()

    feature_file = tmp_project / "docs/features/bad_rule.feature"
    feature_title = "Period Rule"
    rule_title = "Guard.Inspection"

    write_feature(
        tmp_project,
        "bad_rule",
        f"""\
    Feature: {feature_title}

      Rule: {rule_title}
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
    assert violation.error_type == "invalid-rule-title"
    assert "invalid" in violation.message.lower()


def test_scenario_title_with_slash(tmp_project: Path, config: Config) -> None:
    """A Scenario title containing a slash is flagged as invalid-scenario-title."""
    features_root = tmp_project / "docs/features"
    assert features_root.exists()

    feature_file = tmp_project / "docs/features/bad_scenario.feature"
    feature_title = "Forward Slash Scenario"
    scenario_title = "guard/bee/inspects"

    write_feature(
        tmp_project,
        "bad_scenario",
        f"""\
    Feature: {feature_title}

      Scenario: {scenario_title}
        Given a bee
        When it flies
        Then it lands
    """,
    )
    assert feature_file.exists()

    result = validate_all_titles(config)
    assert len(result) == 1
    violation = result[0]
    assert violation.error_type == "invalid-scenario-title"
    assert "invalid" in violation.message.lower()


def test_underscore_is_valid_charset(tmp_project: Path, config: Config) -> None:
    r"""Underscores are valid characters in titles (matching ``\w``)."""
    features_root = tmp_project / "docs/features"
    assert features_root.exists()

    feature_file = tmp_project / "docs/features/underscore.feature"
    feature_title = "Login_Flow Authentication"

    write_feature(
        tmp_project,
        "underscore",
        f"""\
    Feature: {feature_title}

      Scenario: user signs in with email
        Given a user
        When they sign in with email
        Then they are authenticated
    """,
    )
    assert feature_file.exists()

    result = validate_all_titles(config)
    assert len(result) == 0
