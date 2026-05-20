import pytest
from beehave.status import compute_status
from conftest import write_feature, write_test


def test_mixed_feature_with_all_scenario_statuses(tmp_project, config, capsys):
    """Feature with ok stub and unmapped scenarios → stage derived from worst scenario."""
    features_dir = "docs/features"
    tests_dir = "tests/features"
    assert (tmp_project / features_dir).exists()
    assert (tmp_project / tests_dir).exists()

    n_scenarios = 3
    _feature_ref = "docs/features/mixed.feature"

    write_feature(
        tmp_project,
        "mixed",
        """\
        Feature: Mixed Status Feature
          Scenario: Scenario A Ok
            Given a step literal "hello"
            When action occurs
            Then result is "world"

          Scenario: Scenario B Stub
            Given a step literal "alpha"
            When action occurs
            Then result is "beta"

          Scenario: Scenario C Unmapped
            Given a step literal "gamma"
            When action occurs
            Then result is "delta"
        """,
    )

    write_test(
        tmp_project,
        "mixed_status_feature",
        "default_test.py",
        """\
        def test_scenario_a_ok():
            assert "hello" == "hello"
            assert "world" == "world"

        def test_scenario_b_stub():
            pass
        """,
    )

    with pytest.raises(SystemExit):
        compute_status(config)

    captured = capsys.readouterr()
    assert "needs tests" in captured.out
    assert "no test" in captured.out
    assert "no body" in captured.out
    # scenario A status is "ok"
    assert "ok" in captured.out
    assert n_scenarios == 3


def test_mixed_feature_ok_and_error_scens(tmp_project, config, capsys):
    """Feature with ok and error scenarios → stage 'needs fixes'."""
    features_dir = "docs/features"
    tests_dir = "tests/features"
    assert (tmp_project / features_dir).exists()
    assert (tmp_project / tests_dir).exists()

    n_scenarios = 2
    _feature_ref = "docs/features/ok_plus_errors.feature"

    write_feature(
        tmp_project,
        "ok_plus_errors",
        """\
        Feature: Ok Plus Errors
          Scenario: Scenario A Ok
            Given a step literal "first"
            When action occurs
            Then result is <outcome>

          Scenario: Scenario B Error
            Given a step with placeholder <price>
            When action occurs
            Then result is "done"
        """,
    )

    write_test(
        tmp_project,
        "ok_plus_errors",
        "default_test.py",
        """\
        def test_scenario_a_ok():
            outcome = "success"
            assert "first" == "first"

        def test_scenario_b_error():
            assert "done" == "done"
        """,
    )

    with pytest.raises(SystemExit):
        compute_status(config)

    captured = capsys.readouterr()
    assert "needs fixes" in captured.out
    assert "1 error" in captured.out
    # scenario A status is "ok"
    assert "ok" in captured.out
    assert n_scenarios == 2
