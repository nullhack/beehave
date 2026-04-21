"""Tests for report-steps — HTML Acceptance Criteria Column rule."""

import pytest


def test_report_steps_88d58f5c(pytester: pytest.Pytester) -> None:
    """
    Given: pytest-html is installed and show_steps_in_html = true
    And: a test in tests/features/ with a docstring
    When: the pytest-html report is generated
    Then: the "Acceptance Criteria" column contains the verbatim docstring for that test
    """
    # Given
    pytester.makepyprojecttoml(
        "[tool.pytest.ini_options]\nminversion = '6.0'\n"
        "[tool.beehave]\nshow_steps_in_html = true\n"
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
    report_path = pytester.path / "report.html"
    # When
    pytester.runpytest("--html", str(report_path), "--ignore=docs")
    # Then
    assert report_path.exists()
    html_content = report_path.read_text(encoding="utf-8")
    assert "Acceptance Criteria" in html_content
    assert "Given: a condition" in html_content


def test_report_steps_73c4a71a(pytester: pytest.Pytester) -> None:
    """
    Given: pytest-html is installed and show_steps_in_html = true
    And: a test outside tests/features/
    When: the pytest-html report is generated
    Then: the "Acceptance Criteria" column is blank for that test
    """
    # Given
    pytester.makepyprojecttoml(
        "[tool.pytest.ini_options]\nminversion = '6.0'\n"
        "[tool.beehave]\nshow_steps_in_html = true\n"
    )
    pytester.makepyfile(
        **{
            "tests/unit/my_unit_test": (
                "def test_something():\n"
                "    '''\n"
                "    Given: a unit condition\n"
                "    '''\n"
                "    pass\n"
            )
        }
    )
    report_path = pytester.path / "report.html"
    # When
    pytester.runpytest("--html", str(report_path), "--ignore=docs")
    # Then
    assert report_path.exists()
    html_content = report_path.read_text(encoding="utf-8")
    assert "Acceptance Criteria" in html_content
    assert "Given: a unit condition" not in html_content


def test_report_steps_6c592c81(pytester: pytest.Pytester) -> None:
    """
    Given: pytest-html is not installed
    When: pytest runs and generates output
    Then: no "Acceptance Criteria" column appears and no error is raised
    """
    # Given
    pytester.makepyprojecttoml(
        "[tool.pytest.ini_options]\nminversion = '6.0'\n"
        "[tool.beehave]\nshow_steps_in_html = true\n"
    )
    pytester.makepyfile(
        **{
            "tests/features/my_feature/my_rule_test": (
                "def test_my_feature_aabbccdd():\n"
                "    '''\n"
                "    Given: a condition\n"
                "    '''\n"
                "    pass\n"
            )
        }
    )
    # Simulate pytest-html not available by patching _html_available
    pytester.makeconftest(
        "from pytest_beehave import plugin\nplugin._html_available = lambda: False\n"
    )
    report_path = pytester.path / "report.html"
    # When
    result = pytester.runpytest("--html", str(report_path), "--ignore=docs")
    # Then
    assert result.ret == 0
    html_content = report_path.read_text(encoding="utf-8")
    assert "Acceptance Criteria" not in html_content
