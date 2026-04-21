"""Tests for configured path respect story."""

from pathlib import Path

from pytest_beehave.hatch import run_hatch


def test_example_hatch_c3d4e5f6(tmp_path: Path) -> None:
    """
    Given: pyproject.toml contains [tool.beehave] with features_path set to a custom directory
    When: pytest is invoked with --beehave-hatch
    Then: the generated .feature files are written under the custom configured path and not under docs/features/
    """
    custom_path = tmp_path / "my_custom_features"
    default_path = tmp_path / "docs" / "features"

    run_hatch(custom_path, force=False)

    assert list(custom_path.rglob("*.feature"))
    assert not default_path.exists()
