"""Tests for malformed ids are replaced story."""

import pytest


@pytest.mark.skip(reason="not yet implemented")
def test_id_generation_4282d12b() -> None:
    """
    Given: a `.feature` file with an Example tagged `@id:`
    When: beehave assigns IDs
    Then: the malformed tag is replaced with a new valid `@id`
    """
    raise NotImplementedError


@pytest.mark.skip(reason="not yet implemented")
def test_id_generation_553b3cf7() -> None:
    """
    Given: a `.feature` file with an Example tagged `@id:ZZZZZZZZ`
    When: beehave assigns IDs
    Then: the malformed tag is replaced with a new valid `@id`
    """
    raise NotImplementedError

