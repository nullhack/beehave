"""Unit tests for pytest_beehave.config module."""

from pathlib import Path

import pytest

from pytest_beehave.config import (
    DEFAULT_FEATURES_PATH,
    is_explicitly_configured,
    read_stub_format,
    resolve_features_path,
)


def test_resolve_features_path_returns_default_when_no_pyproject(
    tmp_path: Path,
) -> None:
    """
    Given: A project root with no pyproject.toml file
    When: resolve_features_path is called
    Then: The default docs/features path is returned
    """
    # Given
    # (tmp_path has no pyproject.toml)
    # When
    result = resolve_features_path(tmp_path)
    # Then
    assert result == tmp_path / DEFAULT_FEATURES_PATH


def test_is_explicitly_configured_returns_false_when_no_pyproject(
    tmp_path: Path,
) -> None:
    """
    Given: A project root with no pyproject.toml file
    When: is_explicitly_configured is called
    Then: False is returned
    """
    # Given
    # (tmp_path has no pyproject.toml)
    # When
    result = is_explicitly_configured(tmp_path)
    # Then
    assert result is False


def test_read_stub_format_raises_on_invalid_value(tmp_path: Path) -> None:
    """
    Given: A pyproject.toml with stub_format set to an invalid value
    When: read_stub_format is called
    Then: SystemExit is raised with the invalid value in the message
    """
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[tool.beehave]\nstub_format = "methods"\n', encoding="utf-8")
    with pytest.raises(SystemExit, match="methods"):
        read_stub_format(tmp_path)
