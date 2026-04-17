"""Tests for features path config story."""

from pathlib import Path

import pytest

from pytest_beehave.config import resolve_features_path


@pytest.mark.unit
def test_plugin_configuration_acf12157(tmp_path: Path) -> None:
    """
    Given: pyproject.toml contains [tool.beehave] with features_path set to a custom directory
    When: pytest is invoked
    Then: the plugin reads .feature files from the configured custom directory
    """
    # Given
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[tool.beehave]\nfeatures_path = "custom/path"\n')
    # When
    result = resolve_features_path(tmp_path)
    # Then
    assert result == tmp_path / "custom" / "path"


@pytest.mark.unit
def test_plugin_configuration_ce8a95e7(tmp_path: Path) -> None:
    """
    Given: pyproject.toml contains no [tool.beehave] section
    When: pytest is invoked
    Then: the plugin reads .feature files from docs/features/ relative to the project root
    """
    # Given
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[tool.pytest.ini_options]\nminversion = '6.0'\n")
    # When
    result = resolve_features_path(tmp_path)
    # Then
    assert result == tmp_path / "docs" / "features"


@pytest.mark.integration
@pytest.mark.slow
def test_plugin_configuration_124f65e7(pytester: pytest.Pytester) -> None:
    """
    Given: pyproject.toml contains [tool.beehave] with features_path pointing to a non-existent directory
    When: pytest is invoked
    Then: the pytest run exits with a non-zero status code and an error naming the missing path
    """
    # Given
    pytester.makepyprojecttoml('[tool.beehave]\nfeatures_path = "no/such/dir"\n')
    pytester.makepyfile("def test_placeholder(): pass")
    # When
    result = pytester.runpytest()
    # Then
    assert result.ret != 0
    result.stderr.fnmatch_lines(["*no/such/dir*"])


@pytest.mark.unit
def test_plugin_configuration_aaeda817(tmp_path: Path) -> None:
    """
    Given: no pyproject.toml exists in the project root
    When: pytest is invoked
    Then: the plugin reads .feature files from docs/features/ relative to the project root
    """
    # Given
    # (tmp_path has no pyproject.toml)
    # When
    result = resolve_features_path(tmp_path)
    # Then
    assert result == tmp_path / "docs" / "features"
