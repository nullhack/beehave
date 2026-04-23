"""Tests for existing valid ids are preserved story."""

import pytest


@pytest.mark.skip(reason="not yet implemented")
def test_id_generation_d2e63026() -> None:
    """
    Given: a `.feature` file with an Example tagged `@id:custom01`
    When: beehave assigns IDs
    Then: the `@id:custom01` tag is preserved as-is
    """
    raise NotImplementedError


@pytest.mark.skip(reason="not yet implemented")
def test_id_generation_8499105f() -> None:
    """
    Given: a `.feature` file with an Example tagged `@id:a1b2c3d4`
    When: beehave assigns IDs
    Then: the `@id:a1b2c3d4` tag is left unchanged
    """
    raise NotImplementedError

