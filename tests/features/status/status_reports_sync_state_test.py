"""Tests for status reports sync state story."""

import pytest


@pytest.mark.skip(reason="not yet implemented")
def test_status_cc96c609() -> None:
    """
    Given: a project where all stubs match their `.feature` files
    When: the user runs "beehave status"
    Then: the command outputs "OK"
    And: the exit code is 0
    """
    raise NotImplementedError


@pytest.mark.skip(reason="not yet implemented")
def test_status_80e23cea() -> None:
    """
    Given: a project where stubs are out of date with `.feature` files
    When: the user runs "beehave status"
    Then: a summary of what would change is available
    And: the exit code is 1
    """
    raise NotImplementedError

