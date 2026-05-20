import os
import pytest

from beehave.status import compute_status
from beehave.config import Config
from conftest import write_feature, write_test


def test_unmapped_directory_shown_with_flag(tmp_project, config, capsys):
    """Test directory with no matching feature → reported when --include-unmapped."""
    features_dir = "docs/features"
    tests_dir = "tests/features"
    assert (tmp_project / features_dir).exists()
    assert (tmp_project / tests_dir).exists()

    unmapped_path = "tests/features/removed_feature"
    missing_feature = "docs/features/removed_feature.feature"

    # Create a test directory with a test file, but no feature file
    test_dir = tmp_project / "tests" / "features" / "removed_feature"
    test_dir.mkdir(parents=True, exist_ok=True)
    (test_dir / "default_test.py").write_text("def test_something(): pass\n")

    # Verify unmapped path exists and feature file does not
    assert unmapped_path == "tests/features/removed_feature"
    assert not (tmp_project / missing_feature).exists()

    # Create a feature so compute_status doesn't exit 0 with no features
    write_feature(
        tmp_project,
        "exists_only",
        """\
        Feature: Exists Only
          Scenario: Existing Scenario
            Given a step literal "hello"
            When action occurs
            Then result is "world"
        """,
    )
    write_test(
        tmp_project,
        "exists_only",
        "default_test.py",
        """\
        def test_existing_scenario():
            assert "hello" == "hello"
            assert "world" == "world"
        """,
    )

    with pytest.raises(SystemExit):
        compute_status(config, include_unmapped=True)

    captured = capsys.readouterr()
    assert "removed_feature" in captured.out


def test_unmapped_directory_not_shown_without_flag(tmp_project, config, capsys):
    """Without --include-unmapped, unmapped directories are not reported."""
    features_dir = "docs/features"
    tests_dir = "tests/features"
    assert (tmp_project / features_dir).exists()
    assert (tmp_project / tests_dir).exists()

    unmapped_path = "tests/features/removed_feature"
    missing_feature = "docs/features/removed_feature.feature"

    # Create a test directory with a test file, but no feature file
    test_dir = tmp_project / "tests" / "features" / "removed_feature"
    test_dir.mkdir(parents=True, exist_ok=True)
    (test_dir / "default_test.py").write_text("def test_something(): pass\n")

    # Verify unmapped path exists and feature file does not
    assert unmapped_path == "tests/features/removed_feature"
    assert not (tmp_project / missing_feature).exists()

    # Create a feature so compute_status doesn't exit 0 with no features
    write_feature(
        tmp_project,
        "exists_only",
        """\
        Feature: Exists Only
          Scenario: Existing Scenario
            Given a step literal "hello"
            When action occurs
            Then result is "world"
        """,
    )
    write_test(
        tmp_project,
        "exists_only",
        "default_test.py",
        """\
        def test_existing_scenario():
            assert "hello" == "hello"
            assert "world" == "world"
        """,
    )

    with pytest.raises(SystemExit):
        compute_status(config, include_unmapped=False)

    captured = capsys.readouterr()
    assert "removed_feature" not in captured.out
