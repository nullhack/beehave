import pytest

from beehave.status import compute_status
from conftest import write_feature, write_test


def test_two_features_produce_same_function_name(tmp_project, config, capsys):
    """Duplicate function names across features → collision reported."""
    features_dir = "docs/features"
    tests_dir = "tests/features"
    assert (tmp_project / features_dir).exists()
    assert (tmp_project / tests_dir).exists()

    collision_scenario = "login"
    auth_test_path = "tests/features/auth/default_test.py"
    sso_test_path = "tests/features/sso/default_test.py"

    write_feature(
        tmp_project,
        "auth",
        """\
        Feature: Auth Feature
          Scenario: Login
            Given a login page
            When the user logs in
            Then the user is authenticated
        """,
    )
    write_test(
        tmp_project,
        "auth_feature",
        "default_test.py",
        """\
        def test_login():
            pass
        """,
    )

    write_feature(
        tmp_project,
        "sso",
        """\
        Feature: SSO Feature
          Scenario: Login
            Given an sso page
            When the user logs in via sso
            Then the user is authenticated
        """,
    )
    write_test(
        tmp_project,
        "sso_feature",
        "default_test.py",
        """\
        def test_login():
            pass
        """,
    )

    assert collision_scenario == "login"
    assert auth_test_path == "tests/features/auth/default_test.py"
    assert sso_test_path == "tests/features/sso/default_test.py"

    with pytest.raises(SystemExit):
        compute_status(config)

    captured = capsys.readouterr()
    # Collision should be reported
    assert "test_login" in captured.out
    assert "collision" in captured.out


def test_no_collisions_unique_function_names(tmp_project, config, capsys):
    """Unique function names → no collisions reported."""
    features_dir = "docs/features"
    tests_dir = "tests/features"
    assert (tmp_project / features_dir).exists()
    assert (tmp_project / tests_dir).exists()

    auth_functions = ["test_login", "test_logout"]
    payment_functions = ["test_charge", "test_refund"]

    write_feature(
        tmp_project,
        "auth",
        """\
        Feature: Auth Feature
          Scenario: Login
            Given a login page
            When the user logs in
            Then the user is authenticated
          Scenario: Logout
            Given a logged in user
            When the user logs out
            Then the user is logged out
        """,
    )
    write_test(
        tmp_project,
        "auth_feature",
        "default_test.py",
        """\
        def test_login():
            pass

        def test_logout():
            pass
        """,
    )

    write_feature(
        tmp_project,
        "payment",
        """\
        Feature: Payment Feature
          Scenario: Charge
            Given a payment method
            When the charge occurs
            Then the charge is successful
          Scenario: Refund
            Given a previous charge
            When the refund occurs
            Then the refund is successful
        """,
    )
    write_test(
        tmp_project,
        "payment_feature",
        "default_test.py",
        """\
        def test_charge():
            pass

        def test_refund():
            pass
        """,
    )

    assert auth_functions[0] == "test_login"
    assert auth_functions[1] == "test_logout"
    assert payment_functions[0] == "test_charge"
    assert payment_functions[1] == "test_refund"

    with pytest.raises(SystemExit):
        compute_status(config)

    captured = capsys.readouterr()
    assert "collision" not in captured.out
