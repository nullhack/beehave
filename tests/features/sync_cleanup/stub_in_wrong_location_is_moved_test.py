"""Tests for stub in wrong location is moved story."""

import pytest


@pytest.mark.skip(reason="not yet implemented")
def test_sync_cleanup_dc668d29() -> None:
    """
    Given: a test function `test_login_a1b2c3d4` in `tests/features/old_name/`
    And: `@id:a1b2c3d4` maps to feature "new_name"
    When: beehave sync runs
    Then: the function is moved to `tests/features/new_name/`
    And: the test body is preserved
    """
    raise NotImplementedError

