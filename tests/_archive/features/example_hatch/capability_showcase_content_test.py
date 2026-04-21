"""Tests for capability showcase content story."""

from pathlib import Path

import pytest

from pytest_beehave.hatch import run_hatch


@pytest.fixture
def hatched(tmp_path: Path) -> Path:
    """Run hatch into tmp_path and return the features root."""
    features_root = tmp_path / "features"
    run_hatch(features_root, force=False)
    return features_root


def _all_contents(features_root: Path) -> list[str]:
    return [f.read_text(encoding="utf-8") for f in features_root.rglob("*.feature")]


def _has_untagged_example(content: str) -> bool:
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if line.strip().startswith("Example:") and i > 0:
            prev = lines[i - 1].strip()
            if not prev.startswith("@id:"):
                return True
    return False


def test_example_hatch_7a8b9c0d(hatched: Path) -> None:
    """
    Given: no features directory exists at the configured path
    When: pytest is invoked with --beehave-hatch
    Then: at least one generated .feature file contains an Example with no @id tag
    """
    contents = _all_contents(hatched)
    assert any(_has_untagged_example(c) for c in contents)


def test_example_hatch_8b9c0d1e(hatched: Path) -> None:
    """
    Given: no features directory exists at the configured path
    When: pytest is invoked with --beehave-hatch
    Then: at least one generated .feature file contains an Example tagged @deprecated
    """
    contents = _all_contents(hatched)
    assert any("@deprecated" in content for content in contents)


def test_example_hatch_9c0d1e2f(hatched: Path) -> None:
    """
    Given: no features directory exists at the configured path
    When: pytest is invoked with --beehave-hatch
    Then: at least one generated .feature file begins with a # language: directive
    """
    files = list(hatched.rglob("*.feature"))
    assert any(f.read_text(encoding="utf-8").startswith("# language:") for f in files)


def test_example_hatch_0d1e2f3a(hatched: Path) -> None:
    """
    Given: no features directory exists at the configured path
    When: pytest is invoked with --beehave-hatch
    Then: at least one generated .feature file contains a Background: block
    """
    contents = _all_contents(hatched)
    assert any("Background:" in content for content in contents)


def test_example_hatch_1e2f3a4b(hatched: Path) -> None:
    """
    Given: no features directory exists at the configured path
    When: pytest is invoked with --beehave-hatch
    Then: at least one generated .feature file contains a Scenario Outline with an Examples: table
    """
    contents = _all_contents(hatched)
    assert any(
        "Scenario Outline:" in content and "Examples:" in content
        for content in contents
    )


def test_example_hatch_a1f2e3d4(hatched: Path) -> None:
    """
    Given: no features directory exists at the configured path
    When: pytest is invoked with --beehave-hatch
    Then: at least one generated .feature file contains a step followed by a data table
    """
    contents = _all_contents(hatched)
    assert any("| " in content for content in contents)


def test_example_hatch_b2e3d4c5(hatched: Path) -> None:
    """
    Given: no features directory exists at the configured path
    When: pytest is invoked with --beehave-hatch
    Then: at least one generated .feature file is placed in the completed subfolder
    """
    assert list((hatched / "completed").glob("*.feature"))
