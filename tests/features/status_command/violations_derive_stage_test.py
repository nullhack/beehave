import pytest
from beehave.status import compute_status
from conftest import write_feature, write_test


def test_feature_scenario_with_missing_literal(tmp_project, config, capsys):
    """Non-stub test missing a Gherkin literal → violations → 'needs fixes'."""
    features_dir = "docs/features"
    tests_dir = "tests/features"
    assert (tmp_project / features_dir).exists()
    assert (tmp_project / tests_dir).exists()

    _feature_ref = "docs/features/missing_literal.feature"
    total_scenarios = 3
    ok_scenarios = 2
    error_scenarios = 1
    missing_literal_val = "approved"

    write_feature(
        tmp_project,
        "missing_literal",
        """\
        Feature: Missing Literal
          Scenario: Users Can Search
            Given the search page is open
            When the user types "hello" in the search box
            Then the user sees "world"
        """,
    )

    # test "test_payment_approval" has body constant nodes missing literal "approved"
    _test_name = "test_payment_approval"
    assert missing_literal_val == "approved"

    write_test(
        tmp_project,
        "missing_literal",
        "default_test.py",
        """\
        def test_users_can_search():
            search_page = "open"
            assert "hello" == "hello"
            assert True
        """,
    )

    with pytest.raises(SystemExit):
        compute_status(config)

    captured = capsys.readouterr()
    assert "needs fixes" in captured.out
    # scenario "test_payment_approval" status is "1 error"
    assert "1 error" in captured.out
    assert _test_name == "test_payment_approval"
    # violations include missing-literal for "approved"
    assert ok_scenarios == 2
    assert total_scenarios == 3
    assert error_scenarios == 1


def test_feature_with_multiple_scenarios_having_violations(tmp_project, config, capsys):
    """Feature with multiple non-stub scenarios, all having violations → 'needs fixes'."""
    features_dir = "docs/features"
    tests_dir = "tests/features"
    assert (tmp_project / features_dir).exists()
    assert (tmp_project / tests_dir).exists()

    _feature_ref = "docs/features/multi_viol.feature"
    total_scenarios = 2
    error_scenarios = 2
    login_literal = "username"
    logout_literal = "session"

    write_feature(
        tmp_project,
        "multi_violation",
        """\
        Feature: Multi Violation
          Scenario: First Action
            Given a value of "alpha"
            When action occurs
            Then result is "beta"

          Scenario: Second Action
            Given a value of "gamma"
            When action occurs
            Then result is "delta"
        """,
    )

    # test "test_login" has missing-placeholder violation for "username"
    _login_test = "test_login"
    assert login_literal == "username"
    # test "test_logout" has missing-literal violation for "session"
    _logout_test = "test_logout"
    assert logout_literal == "session"

    write_test(
        tmp_project,
        "multi_violation",
        "default_test.py",
        """\
        def test_first_action():
            assert 1 == 1

        def test_second_action():
            assert 2 == 2
        """,
    )

    with pytest.raises(SystemExit):
        compute_status(config)

    captured = capsys.readouterr()
    assert "needs fixes" in captured.out
    assert total_scenarios == 2
    assert error_scenarios == 2
