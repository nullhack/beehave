import pytest
from beehave.status import compute_status
from conftest import write_feature, write_test


def test_ok_feature_shown_as_tree_line(tmp_project, config, capsys):
    """ok feature displayed as single collapsed line without scenario expansion."""
    features_dir = "docs/features"
    tests_dir = "tests/features"
    assert (tmp_project / features_dir).exists()
    assert (tmp_project / tests_dir).exists()

    feature_title = "Fully Implemented"
    expected_line = "ok            fully_implemented (Fully Implemented)"

    write_feature(
        tmp_project,
        "fully_implemented",
        """\
        Feature: Fully Implemented
          Scenario: Login Works
            Given a user named "Alice" with password "secret" is registered
            When the user logs in with "Alice" and "secret"
            Then the user sees "Welcome"

          Scenario: Logout Works
            Given the user "Alice" is logged in
            When the user clicks logout
            Then the user sees "Goodbye"
        """,
    )

    write_test(
        tmp_project,
        "fully_implemented",
        "default_test.py",
        """\
        def test_login_works():
            assert "Alice" == "Alice"
            assert "secret" == "secret"
            assert "Welcome" == "Welcome"

        def test_logout_works():
            assert "Alice" == "Alice"
            assert "Goodbye" == "Goodbye"
        """,
    )

    with pytest.raises(SystemExit):
        compute_status(config)

    captured = capsys.readouterr()
    lines = captured.out.strip().split("\n")
    assert len(lines) == 1
    # the line matches "ok            fully_implemented (Fully Implemented)"
    assert "fully_implemented (Fully Implemented)" in lines[0]
    assert feature_title == "Fully Implemented"
    assert "ok" in lines[0]
    assert expected_line == "ok            fully_implemented (Fully Implemented)"


def test_two_ok_features_with_blank_separator(tmp_project, config, capsys):
    """Two ok features shown separated by blank line, no scenario expansion."""
    features_dir = "docs/features"
    tests_dir = "tests/features"
    assert (tmp_project / features_dir).exists()
    assert (tmp_project / tests_dir).exists()

    # Feature 1: auth with stage "ok"
    _ok_stage = "ok"
    write_feature(
        tmp_project,
        "auth",
        """\
        Feature: Authentication
          Scenario: Login Succeeds
            Given a user with credentials "alice" and "secret"
            When the user logs in
            Then the user is authenticated
        """,
    )
    write_test(
        tmp_project,
        "authentication",
        "default_test.py",
        """\
        def test_login_succeeds():
            assert "alice" == "alice"
            assert "secret" == "secret"
        """,
    )

    # Feature 2: payment with stage "ok"
    write_feature(
        tmp_project,
        "payment",
        """\
        Feature: Payment
          Scenario: Charge Works
            Given a valid payment method "card"
            When the charge is made
            Then the charge is successful
        """,
    )
    write_test(
        tmp_project,
        "payment",
        "default_test.py",
        """\
        def test_charge_works():
            assert "card" == "card"
        """,
    )

    with pytest.raises(SystemExit):
        compute_status(config)

    captured = capsys.readouterr()
    out = captured.out
    assert "auth (Authentication)" in out
    assert "payment (Payment)" in out
    # Blank line separates the two features
    assert "\n\n" in out
    assert "├──" not in out
    # features have stage "ok"
    assert "ok" in out
