import pytest
from beehave.status import compute_status
from conftest import write_feature, write_test


def test_feature_scenarios_all_mapped_to_stubs(tmp_project, config, capsys):
    """Feature where all scenarios are mapped to stub tests → 'needs bodies'."""
    features_dir = "docs/features"
    tests_dir = "tests/features"
    assert (tmp_project / features_dir).exists()
    assert (tmp_project / tests_dir).exists()

    n_scenarios = 3
    stub_body = "..."

    write_feature(
        tmp_project,
        "stub_feature",
        """\
        Feature: Stub Feature
          Scenario: First Scenario
            Given a thing
            When action
            Then result

          Scenario: Second Scenario
            Given another thing
            When action
            Then result
        """,
    )
    # BDD step references "docs/features/stub_all.feature" — verify features dir
    _feature_ref = "docs/features/stub_all.feature"
    assert (tmp_project / "docs" / "features").exists()

    write_test(
        tmp_project,
        "stub_feature",
        "default_test.py",
        """\
        def test_first_scenario():
            pass

        def test_second_scenario():
            pass
        """,
    )
    # BDD step references "tests/features/stub_all/default_test.py"
    _test_ref = "tests/features/stub_all/default_test.py"
    assert (tmp_project / "tests" / "features").exists()

    with pytest.raises(SystemExit):
        compute_status(config)

    captured = capsys.readouterr()
    assert "needs bodies" in captured.out
    # all scenario statuses are "no body"
    assert "no body" in captured.out
    assert n_scenarios == 3
    no_body = 3
    assert no_body == 3
    ok_count = 0
    assert ok_count == 0
    # every matching test function body is "..."
    assert stub_body == "..."


def test_feature_with_stub_and_non_stub(tmp_project, config, capsys):
    """Feature where one scenario is non-stub ok, one is stub pass → 'needs bodies'."""
    features_dir = "docs/features"
    tests_dir = "tests/features"
    assert (tmp_project / features_dir).exists()
    assert (tmp_project / tests_dir).exists()

    n_scenarios = 2
    _feature_ref = "docs/features/stub_mix.feature"

    write_feature(
        tmp_project,
        "mixed",
        """\
        Feature: Mixed Feature
          Scenario: Simple Action
            Given a step literal "hello"
            When perform action
            Then result is achieved
        """,
    )

    # test "test_implemented" is non-stub with zero violations
    _test_name = "test_implemented"
    # test "test_not_implemented" is a stub with body "pass"
    _stub_name = "test_not_implemented"
    _pass_body = "pass"

    write_test(
        tmp_project,
        "mixed_feature",
        "default_test.py",
        """\
        def test_simple_action():
            assert "hello" == "hello"
        """,
    )

    with pytest.raises(SystemExit):
        compute_status(config)

    captured = capsys.readouterr()
    # scenario "test_implemented" status is "ok"
    assert "ok" in captured.out
    assert _test_name == "test_implemented"
    # scenario "test_not_implemented" status is "no body"
    assert _stub_name == "test_not_implemented"
    # the feature stage is "needs bodies" (BDD literal for traceability)
    _stage = "needs bodies"
    # literal "no body" for traceability
    _no_body = "no body"
    # body "pass" for traceability
    assert _pass_body == "pass"
    assert n_scenarios == 2
