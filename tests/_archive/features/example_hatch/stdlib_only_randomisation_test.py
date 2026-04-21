"""Tests for stdlib only randomisation story."""

from pathlib import Path

import pytest

from pytest_beehave.hatch import run_hatch


@pytest.mark.slow
def test_example_hatch_d4e5f6a7(tmp_path: Path) -> None:
    """
    Given: no features directory exists at the configured path
    When: pytest is invoked with --beehave-hatch on two separate occasions with the directory removed between runs
    Then: the Feature name in the generated .feature file differs between the two runs
    """
    import shutil

    features_root = tmp_path / "features"
    seen: set[str] = set()
    # Run up to 20 times; probability of all identical is (1/10)^19 ≈ 0
    for _ in range(20):
        if features_root.exists():
            shutil.rmtree(features_root)
        run_hatch(features_root, force=False)
        backlog_files = list((features_root / "backlog").glob("*.feature"))
        content = backlog_files[0].read_text(encoding="utf-8")
        first_line = content.splitlines()[0]
        seen.add(first_line)
        if len(seen) > 1:
            break

    assert len(seen) > 1


def test_example_hatch_e5f6a7b8(tmp_path: Path) -> None:
    """
    Given: a clean environment with only pytest-beehave installed and no other packages
    When: pytest is invoked with --beehave-hatch
    Then: the hatch completes successfully and no import error or missing-module error is raised
    """
    features_root = tmp_path / "features"
    written = run_hatch(features_root, force=False)
    assert written
