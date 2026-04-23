"""Tests for nest is idempotent and additive story."""

import pytest


@pytest.mark.skip(reason="not yet implemented")
def test_nest_5bba6867() -> None:
    """
    Given: a project that is already fully nested
    When: the user runs "beehave nest"
    Then: no existing files or directories are removed or overwritten
    And: a warning is issued that the project is already nested
    """
    raise NotImplementedError


@pytest.mark.skip(reason="not yet implemented")
def test_nest_9e6d9a7b() -> None:
    """
    Given: a project that has `docs/features/` but not `docs/features/backlog/`
    When: the user runs "beehave nest"
    Then: only the missing directories are created
    And: existing directories and their contents are left unchanged
    """
    raise NotImplementedError


@pytest.mark.skip(reason="not yet implemented")
def test_nest_15d18e4b() -> None:
    """
    Given: a project with unrelated files in `docs/features/`
    When: the user runs "beehave nest"
    Then: the missing subdirectories are created
    And: the unrelated files remain untouched
    """
    raise NotImplementedError

