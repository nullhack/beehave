"""Tests for nest supports   check mode for ci story."""

import pytest


@pytest.mark.skip(reason="not yet implemented")
def test_nest_67075383() -> None:
    """
    Given: a project that is fully nested
    When: the user runs "beehave nest --check"
    Then: the command exits with code 0
    And: no files are modified
    """
    raise NotImplementedError


@pytest.mark.skip(reason="not yet implemented")
def test_nest_c055b222() -> None:
    """
    Given: a project missing `tests/features/`
    When: the user runs "beehave nest --check"
    Then: the command exits with code 1
    """
    raise NotImplementedError

