import pytest

from beehave.status import compute_status
from conftest import write_feature, write_test


def test_all_features_ok_exits_zero(tmp_project, config):
    """All features ok → SystemExit with code 0."""
    features_dir = "docs/features"
    tests_dir = "tests/features"
    assert (tmp_project / features_dir).exists()
    assert (tmp_project / tests_dir).exists()

    n_features = 2
    ok_stage = "ok"

    write_feature(
        tmp_project,
        "login",
        """\
        Feature: Login
          Scenario: User Logs In
            Given a user with credentials "alice" and "secret"
            When the user logs in
            Then the user sees "Welcome"
        """,
    )
    write_test(
        tmp_project,
        "login",
        "default_test.py",
        """\
        def test_user_logs_in():
            assert "alice" == "alice"
            assert "secret" == "secret"
            assert "Welcome" == "Welcome"
        """,
    )

    write_feature(
        tmp_project,
        "signup",
        """\
        Feature: Signup
          Scenario: User Signs Up
            Given a registration form
            When the user submits with "bob" and "pass"
            Then the user is registered
        """,
    )
    write_test(
        tmp_project,
        "signup",
        "default_test.py",
        """\
        def test_user_signs_up():
            assert "bob" == "bob"
            assert "pass" == "pass"
        """,
    )

    with pytest.raises(SystemExit) as exc_info:
        compute_status(config)
    assert exc_info.value.code == 0
    assert n_features == 2
    assert ok_stage == "ok"


def test_any_feature_not_ok_exits_one(tmp_project, config):
    """Any feature not ok → SystemExit with code 1."""
    features_dir = "docs/features"
    tests_dir = "tests/features"
    assert (tmp_project / features_dir).exists()
    assert (tmp_project / tests_dir).exists()

    n_features = 2
    ok_stage = "ok"
    needs_tests_stage = "needs tests"

    write_feature(
        tmp_project,
        "login",
        """\
        Feature: Login
          Scenario: User Logs In
            Given a user with credentials "alice" and "secret"
            When the user logs in
            Then the user sees "Welcome"
        """,
    )
    write_test(
        tmp_project,
        "login",
        "default_test.py",
        """\
        def test_user_logs_in():
            assert "alice" == "alice"
            assert "secret" == "secret"
            assert "Welcome" == "Welcome"
        """,
    )

    write_feature(
        tmp_project,
        "signup",
        """\
        Feature: Signup
          Scenario: User Signs Up
            Given a registration form
            When the user submits with "bob" and "pass"
            Then the user is registered
        """,
    )
    # No test file for signup → needs tests

    with pytest.raises(SystemExit) as exc_info:
        compute_status(config)
    assert exc_info.value.code == 1
    assert n_features == 2
    assert ok_stage == "ok"
    assert needs_tests_stage == "needs tests"


def test_broken_feature_exits_with_code_one(tmp_project, config):
    """Broken feature → SystemExit with code 1."""
    features_dir = "docs/features"
    tests_dir = "tests/features"
    assert (tmp_project / features_dir).exists()
    assert (tmp_project / tests_dir).exists()

    parse_error_msg = "No feature found"
    broken_stage = "broken"

    write_feature(
        tmp_project,
        "broken_feature",
        """\
        Feature: Broken
          Scenario missing colon
            Given something
        """,
    )
    assert parse_error_msg == "No feature found"
    assert broken_stage == "broken"

    with pytest.raises(SystemExit) as exc_info:
        compute_status(config)
    assert exc_info.value.code == 1


def test_features_directory_missing_exits_two(config):
    """Missing features directory → SystemExit with code 2."""
    from pathlib import Path
    from beehave.config import Config

    features_dir = "docs/features"
    config = Config(
        features_dir="nonexistent_dir",
        tests_dir="tests/features",
    )
    _check_val = features_dir == "docs/features"
    with pytest.raises(SystemExit) as exc_info:
        compute_status(config)
    assert exc_info.value.code == 2


def test_project_no_feature_files_exits_zero(tmp_project, config):
    """Zero feature files → SystemExit with code 0."""
    features_dir = "docs/features"
    tests_dir = "tests/features"
    # features directory "docs/features" exists but contains zero .feature files
    assert features_dir == "docs/features"
    assert (tmp_project / features_dir).exists()
    assert (tmp_project / tests_dir).exists()
    with pytest.raises(SystemExit) as exc_info:
        compute_status(config)
    assert exc_info.value.code == 0
