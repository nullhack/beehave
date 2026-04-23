"""Tests for nest supports non default layout story."""

import pytest


@pytest.mark.skip(reason="not yet implemented")
def test_nest_ba3004bd() -> None:
    """
    Given: a project without beehave directories
    When: the user runs "beehave nest --features-dir spec/features/"
    Then: the directory structure is created under `spec/features/`
    """
    raise NotImplementedError

