"""Tests for plugin hook — stub sync runs before collection rule."""

import pytest


def _make_backlog_feature(pytester: pytest.Pytester) -> None:
    """Create a minimal backlog feature file with one @id Example."""
    pytester.makefile(
        ".feature",
        **{
            "docs/features/backlog/my-feature/my-story": (
                "Feature: My feature\n"
                "  @id:aabbccdd\n"
                "  Example: Something happens\n"
                "    Given a condition\n"
                "    When an action\n"
                "    Then an outcome\n"
            )
        },
    )


class TestStubSyncRunsBeforeCollection:
    """Tests for the Stub sync runs before collection Rule."""

    def test_plugin_hook_bde8de30(self, pytester: pytest.Pytester) -> None:
        """
        Given: a project with a backlog feature containing a new Example with an @id tag
        When: pytest is invoked
        Then: the test stub for that Example exists before any tests are collected
        """
        _make_backlog_feature(pytester)
        pytester.makeconftest(
            "def pytest_collectstart(collector):\n"
            "    stub = (\n"
            "        collector.config.rootpath\n"
            "        / 'tests' / 'features' / 'my_feature' / 'examples_test.py'\n"
            "    )\n"
            "    assert stub.exists(), f'Stub not found before collection: {stub}'\n"
        )
        pytester.makepyfile("def test_placeholder(): pass")
        result = pytester.runpytest("--ignore=tests/features/")
        assert result.ret == 0

    def test_plugin_hook_d5824c75(self, pytester: pytest.Pytester) -> None:
        """
        Given: a project with a backlog feature containing a new Example
        When: pytest is invoked
        Then: the terminal output includes a summary of the stub sync actions taken
        """
        _make_backlog_feature(pytester)
        pytester.makepyfile("def test_placeholder(): pass")
        result = pytester.runpytest()
        result.stdout.fnmatch_lines(["*CREATE*examples_test.py*"])

    @pytest.mark.skip(reason="orphan: no matching @id in .feature files")
    def test_plugin_hook_e3a13b58(self) -> None:
        """
        Given: a project where the configured features directory does not exist
        When: pytest is invoked
        Then: pytest completes collection without errors
        """
        raise NotImplementedError
