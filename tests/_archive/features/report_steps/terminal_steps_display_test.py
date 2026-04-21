"""Tests for report-steps — Terminal Steps Display rule."""

import pytest


def test_report_steps_2ba9da81(pytester: pytest.Pytester) -> None:
    """
    Given: a test in tests/features/ with a docstring containing BDD steps
    When: pytest runs with -v
    Then: the docstring is printed verbatim on the line below the test path followed by a blank line
    """
    # Given
    pytester.makepyprojecttoml(
        "[tool.pytest.ini_options]\nminversion = '6.0'\n"
        "[tool.beehave]\nshow_steps_in_terminal = true\n"
    )
    pytester.makepyfile(
        **{
            "tests/features/my_feature/my_rule_test": (
                "def test_my_feature_aabbccdd():\n"
                "    '''\n"
                "    Given: a condition\n"
                "    When: an action\n"
                "    Then: an outcome\n"
                "    '''\n"
                "    pass\n"
            )
        }
    )
    # When
    result = pytester.runpytest("-v", "--ignore=docs")
    # Then
    result.stdout.fnmatch_lines(
        [
            "*Given: a condition*",
            "*When: an action*",
            "*Then: an outcome*",
        ]
    )


def test_report_steps_0869902b(pytester: pytest.Pytester) -> None:
    """
    Given: a test in tests/features/ marked skip with a docstring
    When: pytest runs with -v
    Then: the docstring is printed verbatim below the skipped test path followed by a blank line
    """
    # Given
    pytester.makepyprojecttoml(
        "[tool.pytest.ini_options]\nminversion = '6.0'\n"
        "[tool.beehave]\nshow_steps_in_terminal = true\n"
    )
    pytester.makepyfile(
        **{
            "tests/features/my_feature/my_rule_test": (
                "import pytest\n"
                "@pytest.mark.skip(reason='not yet implemented')\n"
                "def test_my_feature_aabbccdd():\n"
                "    '''\n"
                "    Given: a condition\n"
                "    When: an action\n"
                "    Then: an outcome\n"
                "    '''\n"
                "    pass\n"
            )
        }
    )
    # When
    result = pytester.runpytest("-v", "--ignore=docs")
    # Then
    result.stdout.fnmatch_lines(
        [
            "*Given: a condition*",
        ]
    )


def test_report_steps_99cbca75(pytester: pytest.Pytester) -> None:
    """
    Given: a test in tests/unit/ with a docstring
    When: pytest runs with -v
    Then: no additional output is printed for that test
    """
    # Given
    pytester.makepyprojecttoml(
        "[tool.pytest.ini_options]\nminversion = '6.0'\n"
        "[tool.beehave]\nshow_steps_in_terminal = true\n"
    )
    pytester.makepyfile(
        **{
            "tests/unit/my_unit_test": (
                "def test_something():\n"
                "    '''\n"
                "    Given: a unit condition\n"
                "    When: a unit action\n"
                "    Then: a unit outcome\n"
                "    '''\n"
                "    pass\n"
            )
        }
    )
    # When
    result = pytester.runpytest("-v", "--ignore=docs")
    # Then
    assert "Given: a unit condition" not in result.stdout.str()


def test_report_steps_3c1b6d21(pytester: pytest.Pytester) -> None:
    """
    Given: show_steps_in_terminal = false in pyproject.toml
    And: a test in tests/features/ with a docstring
    When: pytest runs with -v
    Then: no steps are printed for that test
    """
    # Given
    pytester.makepyprojecttoml(
        "[tool.pytest.ini_options]\nminversion = '6.0'\n"
        "[tool.beehave]\nshow_steps_in_terminal = false\n"
    )
    pytester.makepyfile(
        **{
            "tests/features/my_feature/my_rule_test": (
                "def test_my_feature_aabbccdd():\n"
                "    '''\n"
                "    Given: a condition\n"
                "    When: an action\n"
                "    Then: an outcome\n"
                "    '''\n"
                "    pass\n"
            )
        }
    )
    # When
    result = pytester.runpytest("-v", "--ignore=docs")
    # Then
    assert "Given: a condition" not in result.stdout.str()


def test_report_steps_3278cf4d(pytester: pytest.Pytester) -> None:
    """
    Given: show_steps_in_terminal = true in pyproject.toml
    And: a test in tests/features/ with a docstring
    When: pytest runs without any -v flag
    Then: no steps are printed for that test
    """
    # Given
    pytester.makepyprojecttoml(
        "[tool.pytest.ini_options]\nminversion = '6.0'\n"
        "[tool.beehave]\nshow_steps_in_terminal = true\n"
    )
    pytester.makepyfile(
        **{
            "tests/features/my_feature/my_rule_test": (
                "def test_my_feature_aabbccdd():\n"
                "    '''\n"
                "    Given: a condition\n"
                "    When: an action\n"
                "    Then: an outcome\n"
                "    '''\n"
                "    pass\n"
            )
        }
    )
    # When
    result = pytester.runpytest("--ignore=docs")
    # Then
    assert "Given: a condition" not in result.stdout.str()
