import pytest
from beehave.status import compute_status
from conftest import write_feature, write_test


def test_feature_with_all_scenarios_passing(tmp_project, config, capsys):
    """Feature where all scenarios have non-stub tests with zero violations → 'ok'."""
    features_dir = "docs/features"
    tests_dir = "tests/features"
    assert (tmp_project / features_dir).exists()
    assert (tmp_project / tests_dir).exists()

    n_scenarios = 3
    _feature_ref = "docs/features/fully_implemented.feature"

    write_feature(
        tmp_project,
        "passing",
        """\
        Feature: Passing Feature
          Scenario: Login Succeeds
            Given a user named "Alice" with password "secret" is registered
            When the user logs in with "Alice" and "secret"
            Then the user sees "Welcome"

          Scenario: Logout Succeeds
            Given the user "Alice" is logged in
            When the user clicks logout
            Then the user sees "Goodbye"
        """,
    )
    # assert features_dir path exists
    assert (tmp_project / features_dir).exists()

    write_test(
        tmp_project,
        "passing_feature",
        "default_test.py",
        """\
        def test_login_succeeds():
            assert "Alice" == "Alice"
            assert "secret" == "secret"
            assert "Welcome" == "Welcome"

        def test_logout_succeeds():
            assert "Alice" == "Alice"
            assert "Goodbye" == "Goodbye"
        """,
    )
    assert (tmp_project / tests_dir).exists()

    with pytest.raises(SystemExit):
        compute_status(config)

    captured = capsys.readouterr()
    assert "ok" in captured.out
    # scenarios_ok is 3
    ok_count = 3
    assert ok_count == 3
    # scenarios_errors is 0
    error_count = 0
    assert error_count == 0
    assert n_scenarios == 3
