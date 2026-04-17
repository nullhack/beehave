"""Tests for ci id enforcement story."""

import pytest


@pytest.mark.integration
@pytest.mark.slow
def test_auto_id_generation_c4d6d9ce(pytester: pytest.Pytester) -> None:
    """
    Given: a read-only .feature file containing an Example with no @id tag
    When: pytest is invoked
    Then: the pytest run exits with a non-zero status code
    """
    # Given
    feature_file = (
        pytester.path
        / "docs"
        / "features"
        / "in-progress"
        / "my-feature"
        / "my-story.feature"
    )
    feature_file.parent.mkdir(parents=True)
    feature_file.write_text(
        "Feature: My feature\n"
        "  Example: Something happens\n"
        "    Given a condition\n"
        "    When an action\n"
        "    Then an outcome\n"
    )
    feature_file.chmod(0o444)
    pytester.makepyfile("def test_placeholder(): pass")
    # When
    result = pytester.runpytest()
    # Then
    assert result.ret != 0


@pytest.mark.integration
@pytest.mark.slow
def test_auto_id_generation_8b9230d4(pytester: pytest.Pytester) -> None:
    """
    Given: a read-only .feature file containing an Example with no @id tag
    When: pytest is invoked
    Then: the error output names the .feature file path and the Example title that is missing an @id
    """
    # Given
    feature_file = (
        pytester.path
        / "docs"
        / "features"
        / "in-progress"
        / "my-feature"
        / "my-story.feature"
    )
    feature_file.parent.mkdir(parents=True)
    feature_file.write_text(
        "Feature: My feature\n"
        "  Example: Something happens\n"
        "    Given a condition\n"
        "    When an action\n"
        "    Then an outcome\n"
    )
    feature_file.chmod(0o444)
    pytester.makepyfile("def test_placeholder(): pass")
    # When
    result = pytester.runpytest()
    # Then
    result.stdout.fnmatch_lines(["*my-story.feature*"])
    result.stdout.fnmatch_lines(["*Something happens*"])
