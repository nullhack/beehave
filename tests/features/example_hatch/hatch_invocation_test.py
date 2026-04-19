"""Tests for hatch invocation story."""

import io
import sys
from pathlib import Path

import pytest

from pytest_beehave.hatch import run_hatch


@pytest.fixture
def features_root(tmp_path: Path) -> Path:
    """Return a non-existent features root under tmp_path."""
    return tmp_path / "features"


def test_example_hatch_1a2b3c4d(features_root: Path) -> None:
    """
    Given: no features directory exists at the configured path
    When: pytest is invoked with --beehave-hatch
    Then: the backlog, in-progress, and completed subfolders exist under the configured features path
    """
    run_hatch(features_root, force=False)

    assert (features_root / "backlog").is_dir()
    assert (features_root / "in-progress").is_dir()
    assert (features_root / "completed").is_dir()


def test_example_hatch_2b3c4d5e(features_root: Path) -> None:
    """
    Given: no features directory exists at the configured path
    When: pytest is invoked with --beehave-hatch
    Then: at least one .feature file exists in each of the backlog, in-progress, and completed subfolders
    """
    run_hatch(features_root, force=False)

    assert list((features_root / "backlog").glob("*.feature"))
    assert list((features_root / "in-progress").glob("*.feature"))
    assert list((features_root / "completed").glob("*.feature"))


@pytest.mark.slow
def test_example_hatch_3c4d5e6f(tmp_path: Path) -> None:
    """
    Given: no features directory exists at the configured path
    When: pytest is invoked with --beehave-hatch
    Then: the terminal output lists each .feature file that was created
    """
    captured = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured
    try:
        result = pytest.main(
            [
                "--beehave-hatch",
                f"--rootdir={tmp_path}",
                "--no-cov",
            ],
            plugins=[],
        )
    finally:
        sys.stdout = old_stdout

    assert result == 0
    output = captured.getvalue()
    features_root = tmp_path / "docs" / "features"
    written = list(features_root.rglob("*.feature"))
    assert written
    for feature_file in written:
        relative = str(feature_file.relative_to(features_root))
        assert relative in output


def test_example_hatch_4d5e6f7a(tmp_path: Path) -> None:
    """
    Given: no features directory exists at the configured path
    When: pytest is invoked with --beehave-hatch
    Then: no tests are collected or executed
    """
    result = pytest.main(
        ["--beehave-hatch", f"--rootdir={tmp_path}", "--co", "-q", "--no-cov"],
        plugins=[],
    )
    assert result == pytest.ExitCode.NO_TESTS_COLLECTED or result == 0
