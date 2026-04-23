"""Tests for id uniqueness is project wide story."""

import pytest


@pytest.mark.skip(reason="not yet implemented")
def test_id_generation_12a7a112() -> None:
    """
    Given: two `.feature` files each containing `@id:a1b2c3d4`
    When: beehave assigns IDs
    Then: a warning or error is raised depending on configuration
    """
    raise NotImplementedError


@pytest.mark.skip(reason="not yet implemented")
def test_id_generation_9ecaf8b1() -> None:
    """
    Given: a randomly generated ID that already exists in the project
    When: beehave assigns IDs
    Then: a new random ID is generated until unique
    """
    raise NotImplementedError

