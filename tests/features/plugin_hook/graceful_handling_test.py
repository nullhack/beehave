"""Tests for plugin hook — graceful handling rule."""

import pytest


class TestGracefulHandling:
    """Tests for the Graceful handling Rule."""

    def test_plugin_hook_d0f2866d(self, pytester: pytest.Pytester) -> None:
        """
        Given: no pyproject.toml [tool.beehave] section is present and the default docs/features/ directory does not exist
        When: pytest is invoked
        Then: pytest completes collection without errors
        """
        pytester.makepyprojecttoml("[tool.pytest.ini_options]\nminversion = '6.0'\n")
        pytester.makepyfile("def test_placeholder(): pass")
        result = pytester.runpytest()
        assert result.ret == 0
