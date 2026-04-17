"""Tests for pytest lifecycle integration story."""

import pytest


@pytest.mark.integration
@pytest.mark.slow
def test_plugin_hook_bde8de30(pytester: pytest.Pytester) -> None:
    """
    Given: a project with a backlog feature containing a new Example with an @id tag
    When: pytest is invoked
    Then: the test stub for that Example exists before any tests are collected
    """
    # Given
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
    pytester.makeconftest(
        "def pytest_collectstart(collector):\n"
        "    stub = (\n"
        "        collector.config.rootpath\n"
        "        / 'tests' / 'features' / 'my_feature' / 'my_story_test.py'\n"
        "    )\n"
        "    assert stub.exists(), f'Stub not found before collection: {stub}'\n"
    )
    pytester.makepyfile("def test_placeholder(): pass")
    # When
    result = pytester.runpytest("--ignore=tests/features/")
    # Then
    assert result.ret == 0


@pytest.mark.deprecated
@pytest.mark.integration
@pytest.mark.slow
def test_plugin_hook_e3a13b58() -> None:
    """
    Given: a project where the configured features directory does not exist
    When: pytest is invoked
    Then: pytest completes collection without errors
    """
    # Given

    # When

    # Then
    raise NotImplementedError


@pytest.mark.integration
@pytest.mark.slow
def test_plugin_hook_d5824c75(pytester: pytest.Pytester) -> None:
    """
    Given: a project with a backlog feature containing a new Example
    When: pytest is invoked
    Then: the terminal output includes a summary of the stub sync actions taken
    """
    # Given
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
    pytester.makepyfile("def test_placeholder(): pass")
    # When
    result = pytester.runpytest()
    # Then
    result.stdout.fnmatch_lines(["*CREATE*my_story_test.py*"])


@pytest.mark.integration
@pytest.mark.slow
def test_plugin_hook_d0f2866d(pytester: pytest.Pytester) -> None:
    """
    Given: no pyproject.toml [tool.beehave] section is present and the default docs/features/ directory does not exist
    When: pytest is invoked
    Then: pytest completes collection without errors
    """
    # Given
    pytester.makepyprojecttoml("[tool.pytest.ini_options]\nminversion = '6.0'\n")
    pytester.makepyfile("def test_placeholder(): pass")
    # (no docs/features/ directory created)
    # When
    result = pytester.runpytest()
    # Then
    assert result.ret == 0
