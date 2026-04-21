"""Tests for overwrite protection story."""

import io
import sys
from pathlib import Path

import pytest


@pytest.mark.slow
def test_example_hatch_5e6f7a8b(tmp_path: Path) -> None:
    """
    Given: the configured features directory already contains at least one .feature file
    When: pytest is invoked with --beehave-hatch
    Then: the pytest run exits with a non-zero status code and an error naming the conflicting path
    """
    features_root = tmp_path / "docs" / "features"
    existing = features_root / "backlog" / "existing.feature"
    existing.parent.mkdir(parents=True)
    existing.write_text("Feature: existing\n", encoding="utf-8")

    captured = io.StringIO()
    old_stderr = sys.stderr
    sys.stderr = captured
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
        sys.stderr = old_stderr

    assert result == 1
    assert str(existing) in captured.getvalue()


def test_example_hatch_6f7a8b9c(tmp_path: Path) -> None:
    """
    Given: the configured features directory already contains at least one .feature file
    When: pytest is invoked with --beehave-hatch --beehave-hatch-force
    Then: the existing .feature files are replaced with the newly generated hatch content
    """
    from pytest_beehave.hatch import run_hatch

    features_root = tmp_path / "features"
    existing = features_root / "backlog" / "existing.feature"
    existing.parent.mkdir(parents=True)
    existing.write_text("Feature: existing\n", encoding="utf-8")

    run_hatch(features_root, force=True)

    assert not existing.exists()
    assert list(features_root.rglob("*.feature"))
