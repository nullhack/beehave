"""Tests for nest creates required directories on a green field project story."""

import pytest


@pytest.mark.skip(reason="not yet implemented")
def test_nest_bc2403aa() -> None:
    """
    Given: a project without any beehave directories
    When: the user runs "beehave nest"
    Then: the following directories are created with `.gitkeep` files:
      | Path                       |
      | docs/features/             |
      | docs/features/backlog/     |
      | docs/features/in-progress/ |
      | docs/features/completed/   |
      | tests/features/            |
    """
    raise NotImplementedError


@pytest.mark.skip(reason="not yet implemented")
def test_nest_4ec46e2c() -> None:
    """
    Given: a project without `[tool.beehave]` in `pyproject.toml`
    When: the user runs "beehave nest"
    Then: a `[tool.beehave]` snippet is injected into `pyproject.toml`
    """
    raise NotImplementedError

