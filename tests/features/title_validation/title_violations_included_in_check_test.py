"""Tests that check_all includes title validation violations."""

from pathlib import Path

from conftest import write_feature

from beehave.check import check_all
from beehave.config import Config


def test_check_includes_title_and_scenario_violations(
    tmp_project: Path, config: Config
) -> None:
    """check_all returns both title violations and unmapped-scenario violations."""
    features_root = tmp_project / "docs/features"
    assert features_root.exists()

    feature_file = tmp_project / "docs/features/bad_title.feature"
    feature_title = "Bad-Title"
    scenario_title = "simple scenario"

    write_feature(
        tmp_project,
        "bad_title",
        f"""\
    Feature: {feature_title}

      Scenario: {scenario_title}
        Given a guard bee at the hive entrance
        When a visitor bee approaches
        Then the guard bee inspects the visitor
    """,
    )
    assert feature_file.exists()

    # No matching test file is created; check_all will also
    # produce an unmapped-scenario violation.

    result = check_all(config)

    error_types = {v.error_type for v in result}
    assert "invalid-feature-title" in error_types, (
        f"expected invalid-feature-title, got {error_types}"
    )
    assert "unmapped-scenario" in error_types, (
        f"expected unmapped-scenario, got {error_types}"
    )

    title_violations = [
        v
        for v in result
        if v.error_type.startswith("invalid-") or v.error_type.startswith("duplicate-")
    ]
    for tv in title_violations:
        assert not tv.is_warning, (
            f"title violation '{tv.error_type}' should be an error, not a warning"
        )

    bad_title_violations = [
        v for v in result if v.error_type == "invalid-feature-title"
    ]
    assert len(bad_title_violations) == 1
    assert "Bad-Title" in bad_title_violations[0].message
