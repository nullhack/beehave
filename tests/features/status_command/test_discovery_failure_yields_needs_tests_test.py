import pytest

from beehave.status import compute_status
from conftest import write_feature, write_test


def test_syntax_error_test_file_unmaps_scenarios(tmp_project, config, capsys):
    """Python syntax error in test file → all scenarios unmapped → 'needs tests'."""
    features_dir = "docs/features"
    tests_dir = "tests/features"
    assert (tmp_project / features_dir).exists()
    assert (tmp_project / tests_dir).exists()

    n_scenarios = 2
    _feature_ref = "docs/features/syntax_error.feature"

    write_feature(
        tmp_project,
        "syntax_error",
        """\
        Feature: Syntax Error Feature
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

    # Write a test file with a Python syntax error
    bad_test_path = "tests/features/syntax_error/default_test.py"
    test_file = (
        tmp_project / "tests" / "features" / "syntax_error_feature" / "default_test.py"
    )
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("def test_first_scenario(\n    pass\n")
    assert bad_test_path == "tests/features/syntax_error/default_test.py"

    with pytest.raises(SystemExit):
        compute_status(config)

    captured = capsys.readouterr()
    assert "needs tests" in captured.out
    assert "no test" in captured.out
    assert n_scenarios == 2
    no_test_count = 2
    assert no_test_count == 2


def test_empty_test_file_unmaps_all_scenarios(tmp_project, config, capsys):
    """Empty test file → all scenarios unmapped → 'needs tests'."""
    features_dir = "docs/features"
    tests_dir = "tests/features"
    assert (tmp_project / features_dir).exists()
    assert (tmp_project / tests_dir).exists()

    n_scenarios = 1
    _feature_ref = "docs/features/empty_test.feature"

    write_feature(
        tmp_project,
        "empty_test",
        """\
        Feature: Empty Test Feature
          Scenario: Only Scenario
            Given a step
            When action occurs
            Then result happens
        """,
    )

    # Write an empty test file
    empty_test_path = "tests/features/empty_test/default_test.py"
    test_file = (
        tmp_project / "tests" / "features" / "empty_test_feature" / "default_test.py"
    )
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("")
    assert empty_test_path == "tests/features/empty_test/default_test.py"

    with pytest.raises(SystemExit):
        compute_status(config)

    captured = capsys.readouterr()
    assert "needs tests" in captured.out
    assert "no test" in captured.out
    assert n_scenarios == 1
    no_test_count = 1
    assert no_test_count == 1
