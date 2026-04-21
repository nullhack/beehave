"""Tests for cache updated after write story."""

import pytest


@pytest.mark.skip(reason="not yet implemented")
def test_incremental_sync_a8d4e7f2() -> None:
    """
    Given: a .feature file that required a new @id tag to be written
    When: pytest completes the sync
    Then: the cache entry for that .feature file contains the mtime and size of the written file
    """
    raise NotImplementedError


@pytest.mark.skip(reason="not yet implemented")
def test_incremental_sync_b3c9f1e6() -> None:
    """
    Given: a stub file that was created or updated during sync
    When: pytest completes the sync
    Then: the cache entry for that stub file contains the mtime and size of the written file
    """
    raise NotImplementedError


@pytest.mark.skip(reason="not yet implemented")
def test_incremental_sync_c7a2d5b8() -> None:
    """
    Given: a .feature file that required a write but the write operation failed
    When: pytest completes the sync
    Then: the cache entry for that .feature file is not updated
    """
    raise NotImplementedError
