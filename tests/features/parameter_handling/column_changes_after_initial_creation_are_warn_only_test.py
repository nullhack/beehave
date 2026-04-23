"""Tests for column changes after initial creation are warn only story."""

import pytest


@pytest.mark.skip(reason="not yet implemented")
def test_parameter_handling_2ff2a0f5() -> None:
    """
    Given: an existing parametrised stub for a Scenario Outline
    And: a new column "email" is added to the Scenario Outline
    When: beehave sync runs
    Then: a warning is issued: "manual intervention required"
    And: the parametrize decorator is NOT updated
    """
    raise NotImplementedError

