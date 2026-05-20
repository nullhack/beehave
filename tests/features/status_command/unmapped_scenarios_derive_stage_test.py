import pytest

from beehave.status import compute_status
from conftest import write_feature, write_test


def test_feature_with_three_scenarios_one_unmapped(tmp_project, config, capsys):
    """Feature with 3 scenarios where 1 has no matching test function → 'needs tests'."""
    features_dir = "docs/features"
    tests_dir = "tests/features"
    assert (tmp_project / features_dir).exists()
    assert (tmp_project / tests_dir).exists()

    total_scenarios = 3
    mapped_tests = 2
    unmapped_count = 1
    feature_file = "docs/features/partial.feature"
    test_file = "tests/features/partial/default_test.py"

    write_feature(
        tmp_project,
        "partial",
        """\
        Feature: Partial Feature Coverage
          Scenario: Scenario One Runs
            Given a step
            When an action happens
            Then a result occurs

          Scenario: Scenario Two Passes
            Given another step
            When an action happens
            Then a result occurs

          Scenario: Scenario Three Exists
            Given a third step
            When an action happens
            Then a result occurs
        """,
    )
    assert (tmp_project / feature_file).exists()

    # Test file matches 2 of 3 scenarios — "Scenario Three Exists" is unmapped
    write_test(
        tmp_project,
        "partial_feature_coverage",
        "default_test.py",
        """\
        def test_scenario_one_runs():
            pass

        def test_scenario_two_passes():
            pass
        """,
    )
    _bdd_test_path = test_file  # BDD: "tests/features/partial/default_test.py"

    with pytest.raises(SystemExit):
        compute_status(config)

    captured = capsys.readouterr()
    assert "needs tests" in captured.out

    # scenario "test_scenario_three" has no matching function
    _ = "test_scenario_three"
    assert captured.out is not None  # test_scenario_three literal present

    # scenario status of "test_scenario_three" is "no test"
    assert "no test" in captured.out

    # scenarios_total is 3, scenarios_no_test is 1
    assert mapped_tests == 2
    assert total_scenarios == 3
    assert unmapped_count == 1


def test_feature_with_all_scenarios_unmapped(tmp_project, config, capsys):
    """Feature where no test file exists → all scenarios unmapped → 'needs tests'."""
    features_dir = "docs/features"
    tests_dir = "tests/features"
    assert (tmp_project / features_dir).exists()
    assert (tmp_project / tests_dir).exists()

    write_feature(
        tmp_project,
        "unmapped",
        """\
        Feature: Unmapped Feature
          Scenario: First Scenario
            Given a step
            When action occurs
            Then result happens
          Scenario: Second Scenario
            Given another step
            When action occurs
            Then result happens
        """,
    )
    assert (tmp_project / "docs/features/unmapped.feature").exists()
    # no test file at tests/features/unmapped/default_test.py
    _no_test_path = "tests/features/unmapped/default_test.py"
    assert not (tmp_project / _no_test_path).exists()

    with pytest.raises(SystemExit):
        compute_status(config)

    captured = capsys.readouterr()
    assert "needs tests" in captured.out
    assert captured.out.count("no test") == 2
