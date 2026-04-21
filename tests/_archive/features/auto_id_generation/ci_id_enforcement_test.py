"""Tests for auto id generation — CI ID enforcement rule."""

import pytest


def _make_readonly_feature(pytester: pytest.Pytester) -> None:
    """Create a read-only feature file with one untagged Example."""
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


class TestCiIdEnforcement:
    """Tests for the CI ID enforcement Rule."""

    def test_ci_id_enforcement_c4d6d9ce(self, pytester: pytest.Pytester) -> None:
        """
        Given: a read-only .feature file containing an Example with no @id tag
        When: pytest is invoked
        Then: the pytest run exits with a non-zero status code
        """
        _make_readonly_feature(pytester)
        result = pytester.runpytest()
        assert result.ret != 0

    def test_ci_id_enforcement_8b9230d4(self, pytester: pytest.Pytester) -> None:
        """
        Given: a read-only .feature file containing an Example with no @id tag
        When: pytest is invoked
        Then: the error output names the .feature file path and the Example title that is missing an @id
        """
        _make_readonly_feature(pytester)
        result = pytester.runpytest()
        result.stdout.fnmatch_lines(["*my-story.feature*"])
        result.stdout.fnmatch_lines(["*Something happens*"])
