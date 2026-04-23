"""Tests for pytest deprecated marker story."""

import pytest


@pytest.mark.skip(reason="not yet implemented")
def test_pytest_adapter_6bcbd28d() -> None:
    """
    Given: the pytest adapter is active
    And: an Example tagged `@deprecated`
    When: beehave sync runs
    Then: the stub is decorated with `@pytest.mark.deprecated`
    """
    raise NotImplementedError

