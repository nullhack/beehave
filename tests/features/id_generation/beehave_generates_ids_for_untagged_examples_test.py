"""Tests for beehave generates ids for untagged examples story."""

import pytest


@pytest.mark.skip(reason="not yet implemented")
def test_id_generation_f888a23f() -> None:
    """
    Given: a `.feature` file with an Example that has no `@id` tag
    When: beehave assigns IDs
    Then: the Example receives an `@id:<8-char-hex>` tag
    And: the tag is a valid 8-character lowercase hex string
    """
    raise NotImplementedError


@pytest.mark.skip(reason="not yet implemented")
def test_id_generation_ec32fe63() -> None:
    """
    Given: a `.feature` file with three Examples without `@id` tags
    When: beehave assigns IDs
    Then: each Example receives a distinct `@id` tag
    """
    raise NotImplementedError

