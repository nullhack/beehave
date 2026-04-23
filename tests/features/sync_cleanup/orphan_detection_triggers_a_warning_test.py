"""Tests for orphan detection triggers a warning story."""

import pytest


@pytest.mark.skip(reason="not yet implemented")
def test_sync_cleanup_5390072a() -> None:
    """
    Given: a test function `test_login_a1b2c3d4` with no matching `@id:a1b2c3d4` in any `.feature` file
    When: beehave sync runs
    Then: a warning is issued about the orphaned stub
    And: the stub is left completely unchanged
    """
    raise NotImplementedError


@pytest.mark.skip(reason="not yet implemented")
def test_sync_cleanup_1a40571d() -> None:
    """
    Given: a `.feature` file is deleted
    And: stubs exist for Examples from that file
    When: beehave sync runs
    Then: the stubs are identified as orphans and warnings are issued
    """
    raise NotImplementedError

