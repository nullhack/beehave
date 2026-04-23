"""Tests for markers come from the adapter story."""

import pytest


@pytest.mark.skip(reason="not yet implemented")
def test_sync_create_8cb2dd6a() -> None:
    """
    Given: the pytest adapter provides skip and deprecated marker templates
    When: beehave sync runs
    Then: the generated stubs use the adapter-provided markers
    """
    raise NotImplementedError

