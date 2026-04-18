"""Tests for features path config story."""

from pathlib import Path

import pytest

from pytest_beehave.config import resolve_features_path


class TestCustomFeaturesPath:
    """Tests for the Custom features path Rule."""

    def test_features_path_config_acf12157(self, tmp_path: Path) -> None:
        """
        Given: pyproject.toml contains [tool.beehave] with features_path set to a custom directory
        When: pytest is invoked
        Then: the plugin reads .feature files from the configured custom directory
        """
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[tool.beehave]\nfeatures_path = "custom/path"\n')
        result = resolve_features_path(tmp_path)
        assert result == tmp_path / "custom" / "path"

    def test_features_path_config_124f65e7(self, pytester: pytest.Pytester) -> None:
        """
        Given: pyproject.toml contains [tool.beehave] with features_path pointing to a non-existent directory
        When: pytest is invoked
        Then: the pytest run exits with a non-zero status code and an error naming the missing path
        """
        pytester.makepyprojecttoml('[tool.beehave]\nfeatures_path = "no/such/dir"\n')
        pytester.makepyfile("def test_placeholder(): pass")
        result = pytester.runpytest()
        assert result.ret != 0
        result.stderr.fnmatch_lines(["*no/such/dir*"])


class TestDefaultFeaturesPath:
    """Tests for the Default features path Rule."""

    def test_features_path_config_ce8a95e7(self, tmp_path: Path) -> None:
        """
        Given: pyproject.toml contains no [tool.beehave] section
        When: pytest is invoked
        Then: the plugin reads .feature files from docs/features/ relative to the project root
        """
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[tool.pytest.ini_options]\nminversion = '6.0'\n")
        result = resolve_features_path(tmp_path)
        assert result == tmp_path / "docs" / "features"

    def test_features_path_config_aaeda817(self, tmp_path: Path) -> None:
        """
        Given: no pyproject.toml exists in the project root
        When: pytest is invoked
        Then: the plugin reads .feature files from docs/features/ relative to the project root
        """
        result = resolve_features_path(tmp_path)
        assert result == tmp_path / "docs" / "features"
