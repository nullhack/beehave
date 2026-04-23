"""Tests for @deprecated marker is added or removed story."""

import pytest


@pytest.mark.skip(reason="not yet implemented")
def test_sync_update_70ab8602() -> None:
    """
    Given: an existing stub without a deprecated marker
    And: the corresponding Example gains `@deprecated`
    When: beehave sync runs
    Then: the deprecated marker from the adapter is added to the stub
    """
    raise NotImplementedError


@pytest.mark.skip(reason="not yet implemented")
def test_sync_update_f3e0cbc2() -> None:
    """
    Given: an existing stub with a deprecated marker
    And: the corresponding Example loses `@deprecated`
    When: beehave sync runs
    Then: the deprecated marker is removed from the stub
    """
    raise NotImplementedError

