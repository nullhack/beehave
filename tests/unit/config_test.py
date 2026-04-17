"""Unit tests for pytest_beehave.config module."""

from pathlib import Path

import pytest

from pytest_beehave.config import (
    DEFAULT_FEATURES_PATH,
    is_explicitly_configured,
    resolve_features_path,
)


@pytest.mark.unit
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


@pytest.mark.unit
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
