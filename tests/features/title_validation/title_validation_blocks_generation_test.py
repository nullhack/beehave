"""Tests that title validation acts as a pre-flight gate during generation."""

import sys
from io import StringIO
from pathlib import Path

import pytest
from conftest import write_feature

from beehave.config import Config
from beehave.generate import generate_stubs


def test_preflight_blocks_generation(tmp_project: Path, config: Config) -> None:
    """generate_stubs refuses to run when title validation finds violations."""
    features_root = tmp_project / "docs/features"
    assert features_root.exists()

    # Given: a valid feature file
    write_feature(
        tmp_project,
        "hive_activity",
        """\
    Feature: Hive Activity

      Scenario: guard bee inspects visitor
        Given a guard bee at the hive entrance
        When a visitor bee approaches
        Then the guard bee inspects the visitor
    """,
    )

    # And: a feature file with an invalid title ("Invalid" has 1 word,
    # failing the 2-6 word count rule; validate_all_titles will flag it)
    write_feature(
        tmp_project,
        "bad_title",
        """\
    Feature: Invalid

      Scenario: some scenario
        Given a guard bee at the hive entrance
        When a visitor bee approaches
        Then the guard bee inspects the visitor
    """,
    )

    # Ensure no stale test output from prior runs
    tests_root = tmp_project / "tests" / "features"
    hive_test_dir = tests_root / "hive_activity"

    captured = StringIO()
    saved_stderr = sys.stderr
    sys.stderr = captured

    try:
        with pytest.raises(SystemExit) as exc_info:
            generate_stubs("hive_activity", config)
        assert exc_info.value.code == 1, (
            "generate_stubs must exit with code 1 when pre-flight title "
            "validation fails"
        )
    finally:
        sys.stderr = saved_stderr

    # Then: the output contains a violation for the invalid title
    output = captured.getvalue()
    assert "Invalid" in output, "expected violation for 'Invalid' in stderr output"

    # And: no test files or directories are created for hive_activity.feature
    assert not hive_test_dir.exists(), (
        "no test files or directories must be created when pre-flight fails"
    )
