"""Tests for @deprecated is propagated as adapter specific marker story."""

import pytest


@pytest.mark.skip(reason="not yet implemented")
def test_deprecation_sync_d3f502c3() -> None:
    """
    Given: the pytest adapter is active
    And: an Example is affected by `@deprecated`
    When: beehave sync runs
    Then: the stub is decorated with `@pytest.mark.deprecated`
    """
    raise NotImplementedError

