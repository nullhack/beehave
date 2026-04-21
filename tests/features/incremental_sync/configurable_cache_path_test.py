"""Tests for configurable cache path story."""

import pytest


@pytest.mark.skip(reason="not yet implemented")
def test_incremental_sync_f9c3a7d5() -> None:
    """
    Given: pyproject.toml contains [tool.beehave] cache_path = ".tmp/beehave-cache"
    When: pytest completes the sync
    Then: the cache file is written to .tmp/beehave-cache/sync_state.json
    And: no file is written to the default .beehave-cache/ directory
    """
    raise NotImplementedError


@pytest.mark.skip(reason="not yet implemented")
def test_incremental_sync_a4e8b2f1() -> None:
    """
    Given: pyproject.toml contains no cache_path key under [tool.beehave]
    When: pytest completes the sync
    Then: the cache file is written to .beehave-cache/sync_state.json relative to the project root
    """
    raise NotImplementedError
