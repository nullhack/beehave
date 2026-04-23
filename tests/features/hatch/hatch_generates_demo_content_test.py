"""Tests for hatch generates demo content story."""

import pytest


@pytest.mark.skip(reason="not yet implemented")
def test_hatch_a7c702b7() -> None:
    """
    Given: a newly nested project with no `.feature` files
    When: the user runs "beehave hatch"
    Then: one or two bee-themed `.feature` files are created in `docs/features/`
    And: each file demonstrates common Gherkin patterns: Feature, Rule, Example, and Scenario Outline
    """
    raise NotImplementedError


@pytest.mark.skip(reason="not yet implemented")
def test_hatch_91b8e512() -> None:
    """
    Given: a project with hatch-generated `.feature` files
    When: the user runs "beehave sync"
    Then: stubs are generated for all Examples in the demo files
    """
    raise NotImplementedError

