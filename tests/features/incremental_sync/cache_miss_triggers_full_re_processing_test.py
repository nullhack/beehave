"""Tests for cache miss triggers full re processing story."""

import pytest


@pytest.mark.skip(reason="not yet implemented")
def test_incremental_sync_d9e3b7a4() -> None:
    """
    Given: a valid cache file exists for a .feature file
    And: the .feature file's mtime has changed since the cache was written
    When: pytest is invoked
    Then: the .feature file is fully re-processed by the sync engine
    """
    raise NotImplementedError


@pytest.mark.skip(reason="not yet implemented")
def test_incremental_sync_e5c8f2d1() -> None:
    """
    Given: a valid cache file exists for a .feature file
    And: the .feature file's size has changed since the cache was written
    When: pytest is invoked
    Then: the .feature file is fully re-processed by the sync engine
    """
    raise NotImplementedError


@pytest.mark.skip(reason="not yet implemented")
def test_incremental_sync_f1b6a3c9() -> None:
    """
    Given: a valid cache file exists but does not contain an entry for a particular .feature file
    When: pytest is invoked
    Then: that .feature file is fully re-processed by the sync engine
    """
    raise NotImplementedError
