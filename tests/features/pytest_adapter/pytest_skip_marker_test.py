"""Tests for pytest skip marker story."""

import pytest


@pytest.mark.skip(reason="not yet implemented")
def test_pytest_adapter_8cd24faa() -> None:
    """
    Given: the pytest adapter is active
    And: an unstubbed Example
    When: beehave sync runs
    Then: the stub is decorated with `@pytest.mark.skip(reason="not yet implemented")`
    """
    raise NotImplementedError

