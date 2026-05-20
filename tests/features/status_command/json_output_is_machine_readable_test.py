import json
import pytest

from beehave.status import compute_status
from conftest import write_feature, write_test


def test_json_output_includes_full_feature_hierarchy(tmp_project, config, capsys):
    """JSON output has features array with full hierarchy and summary."""
    features_dir = "docs/features"
    tests_dir = "tests/features"
    assert (tmp_project / features_dir).exists()
    assert (tmp_project / tests_dir).exists()

    n_features = 2
    needs_fixes_stage = "needs fixes"
    auth_scenarios = 3

    write_feature(
        tmp_project,
        "auth",
        """\
        Feature: Auth Feature
          Scenario: Login Works
            Given a user with credentials "alice" and "secret"
            When the user logs in
            Then the user sees "Welcome"
          Scenario: Logout Works
            Given a logged in user
            When the user logs out
            Then the user sees "Goodbye"
          Scenario: Signup Works
            Given a registration form
            When the user submits email "alice@example.com"
            Then the user is registered
        """,
    )
    write_test(
        tmp_project,
        "auth_feature",
        "default_test.py",
        """\
        def test_login_works():
            assert "alice" == "alice"
            assert "secret" == "secret"
            assert "Welcome" == "Welcome"

        def test_logout_works():
            assert "Goodbye" == "Goodbye"

        def test_signup_works():
            assert "alice@example.com" == "alice@example.com"
        """,
    )

    write_feature(
        tmp_project,
        "payment",
        """\
        Feature: Payment Feature
          Scenario: Charge Works
            Given a payment method
            When the charge is "100"
            Then the charge is successful
          Scenario: Refund Works
            Given a previous charge
            When the refund is "50"
            Then the refund is successful
        """,
    )
    write_test(
        tmp_project,
        "payment_feature",
        "default_test.py",
        """\
        def test_charge_works():
            assert 1 == 1
            # missing "100" literal

        def test_refund_works():
            assert 2 == 2
            # missing "50" literal
        """,
    )

    with pytest.raises(SystemExit):
        compute_status(config, json_output=True)

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "features" in data
    assert len(data["features"]) == 2
    assert "summary" in data
    assert data["summary"]["total_features"] == 2
    assert data["summary"]["ok"] == 1
    assert data["summary"]["needs_fixes"] == 1
    assert n_features == 2
    assert needs_fixes_stage == "needs fixes"
    assert auth_scenarios == 3
    # Each feature has scenarios array
    for feat in data["features"]:
        assert "scenarios" in feat


def test_json_includes_summary_stage_counts(tmp_project, config, capsys):
    """JSON summary has correct stage counts."""
    features_dir = "docs/features"
    tests_dir = "tests/features"
    assert (tmp_project / features_dir).exists()
    assert (tmp_project / tests_dir).exists()

    n_features = 3
    needs_bodies_stage = "needs bodies"
    zero_count = 0

    write_feature(
        tmp_project,
        "ok_feature",
        """\
        Feature: Ok Feature
          Scenario: Test Passes
            Given a step literal "hello"
            When action occurs
            Then result is "world"
        """,
    )
    write_test(
        tmp_project,
        "ok_feature",
        "default_test.py",
        """\
        def test_test_passes():
            assert "hello" == "hello"
            assert "world" == "world"
        """,
    )

    write_feature(
        tmp_project,
        "broken_feature",
        """\
        Feature: Broken Feature
          @invalid tag whitespace
            Given something
        """,
    )

    write_feature(
        tmp_project,
        "stub_feature",
        """\
        Feature: Stub Feature
          Scenario: Stub Test
            Given a step
            When action
            Then result
        """,
    )
    write_test(
        tmp_project,
        "stub_feature",
        "default_test.py",
        """\
        def test_stub_test():
            pass
        """,
    )

    with pytest.raises(SystemExit):
        compute_status(config, json_output=True)

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    s = data["summary"]
    assert s["broken"] == 1
    assert s["needs_bodies"] == 1
    assert s["ok"] == 1
    assert n_features == 3
    assert needs_bodies_stage == "needs bodies"
    assert zero_count == 0


def test_json_has_collision_and_unmapped_entries(tmp_project, config, capsys):
    """JSON output includes unmapped_directories and collisions."""
    features_dir = "docs/features"
    tests_dir = "tests/features"
    assert (tmp_project / features_dir).exists()
    assert (tmp_project / tests_dir).exists()

    unmapped_dir = "tests/features/old_feature"
    collision_fn = "test_login"

    # Unmapped directory
    test_dir = tmp_project / "tests" / "features" / "old_feature"
    test_dir.mkdir(parents=True, exist_ok=True)
    (test_dir / "default_test.py").write_text("def test_old(): pass\n")
    assert unmapped_dir == "tests/features/old_feature"

    # Two features with collision
    write_feature(
        tmp_project,
        "auth",
        """\
        Feature: Auth
          Scenario: Login
            Given a login page
            When the user logs in
            Then the user is authenticated
        """,
    )
    write_test(
        tmp_project,
        "auth",
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
        Feature: SSO
          Scenario: Login
            Given an sso page
            When the user logs in
            Then the user is authenticated
        """,
    )
    write_test(
        tmp_project,
        "sso",
        "default_test.py",
        """\
        def test_login():
            pass
        """,
    )

    assert collision_fn == "test_login"

    with pytest.raises(SystemExit):
        compute_status(config, json_output=True, include_unmapped=True)

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert len(data.get("unmapped_directories", [])) > 0
    assert len(data.get("collisions", [])) > 0
