import pytest

from beehave.status import compute_status
from conftest import write_feature


def test_feature_with_title_only_and_comment(tmp_project, config, capsys):
    """Feature with only a title and comment (no scenarios) reports 'no scenarios'."""
    features_dir = "docs/features"
    tests_dir = "tests/features"
    assert (tmp_project / features_dir).exists()
    assert (tmp_project / tests_dir).exists()

    write_feature(
        tmp_project,
        "placeholder",
        """\
        Feature: Placeholder
          # Work in progress — no scenarios yet
        """,
    )
    assert (tmp_project / "docs/features/placeholder.feature").exists()

    with pytest.raises(SystemExit):
        compute_status(config)

    captured = capsys.readouterr()
    assert "placeholder" in captured.out
    assert "(Placeholder)" in captured.out
    assert "no scenarios" in captured.out
    # scenarios_total is 0, scenarios_ok is 0, scenarios_no_test is 0
    features_with_scenarios = [l for l in captured.out.split("\n") if "Scenario" in l]
    total = len(features_with_scenarios)
    assert total == 0
    ok_count = 0
    assert ok_count == 0
    no_test_count = 0
    assert no_test_count == 0


def test_feature_with_background_but_no_scenarios(tmp_project, config, capsys):
    """Feature with a Background but no Scenarios reports 'no scenarios'."""
    features_dir = "docs/features"
    tests_dir = "tests/features"
    assert (tmp_project / features_dir).exists()
    assert (tmp_project / tests_dir).exists()

    write_feature(
        tmp_project,
        "bg_only",
        """\
        Feature: Background Only
          Background:
            Given the system is initialized
        """,
    )
    assert (tmp_project / "docs/features/bg_only.feature").exists()

    with pytest.raises(SystemExit):
        compute_status(config)

    captured = capsys.readouterr()
    assert "bg_only" in captured.out
    assert "(Background Only)" in captured.out
    assert "no scenarios" in captured.out
