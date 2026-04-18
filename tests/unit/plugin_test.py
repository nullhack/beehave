"""Unit tests for pytest_beehave.plugin module."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from pytest_beehave.plugin import features_path_key, pytest_configure


def test_pytest_configure_stores_resolved_path_when_path_exists(
    tmp_path: Path,
) -> None:
    """
    Given: A project root with a valid features directory
    When: pytest_configure is called
    Then: The resolved path is stored in config.stash
    """
    # Given
    features_dir = tmp_path / "docs" / "features"
    features_dir.mkdir(parents=True)
    mock_config = MagicMock(spec=pytest.Config)
    mock_config.rootpath = tmp_path
    mock_config.stash = {}
    # When
    pytest_configure(mock_config)
    # Then
    assert mock_config.stash[features_path_key] == features_dir
