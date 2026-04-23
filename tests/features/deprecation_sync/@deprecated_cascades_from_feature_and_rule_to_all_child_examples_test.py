"""Tests for @deprecated cascades from feature and rule to all child examples story."""

import pytest


@pytest.mark.skip(reason="not yet implemented")
def test_deprecation_sync_c1f44d6c() -> None:
    """
    Given: a Feature tagged `@deprecated` with three Examples
    When: beehave sync runs
    Then: all three corresponding stubs receive the deprecated marker
    """
    raise NotImplementedError


@pytest.mark.skip(reason="not yet implemented")
def test_deprecation_sync_3f9939c1() -> None:
    """
    Given: a Rule tagged `@deprecated` with two Examples
    When: beehave sync runs
    Then: both corresponding stubs receive the deprecated marker
    """
    raise NotImplementedError


@pytest.mark.skip(reason="not yet implemented")
def test_deprecation_sync_7e966f90() -> None:
    """
    Given: a Feature tagged `@deprecated`
    And: an Example under it that should not be deprecated
    When: beehave sync runs
    Then: the Example's stub still receives the deprecated marker
    """
    raise NotImplementedError

