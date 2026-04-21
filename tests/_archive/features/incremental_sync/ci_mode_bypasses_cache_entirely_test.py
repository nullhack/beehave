"""Tests for ci mode bypasses cache entirely story."""

import pytest


@pytest.mark.skip(reason="not yet implemented")
def test_incremental_sync_b8e4f3a1() -> None:
    """
    Given: the plugin detects a read-only filesystem (CI environment)
    When: pytest is invoked
    Then: the cache file is not read and all files are fully processed
    """
    raise NotImplementedError


@pytest.mark.skip(reason="not yet implemented")
def test_incremental_sync_c3f9d2b6() -> None:
    """
    Given: the plugin detects a read-only filesystem (CI environment)
    When: pytest completes the sync
    Then: the cache file is not created or modified
    """
    raise NotImplementedError
