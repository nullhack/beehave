"""Unit tests for pytest_beehave.plugin module."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pytest_beehave.plugin import _html_available, features_path_key, pytest_configure
from pytest_beehave.steps_reporter import StepsReporter


def test_pytest_configure_stores_resolved_path_when_path_exists(
    tmp_path: Path,
) -> None:
    """
    Given: A project root with a valid features directory
    When: pytest_configure is called
    Then: The resolved path is stored in config.stash
    """
    # Given
    features_dir = tmp_path / "docs" / "features"
    features_dir.mkdir(parents=True)
    mock_config = MagicMock(spec=pytest.Config)
    mock_config.rootpath = tmp_path
    mock_config.stash = {}
    mock_config.pluginmanager = MagicMock()
    mock_config.getoption.return_value = False
    # When
    pytest_configure(mock_config)
    # Then
    assert mock_config.stash[features_path_key] == features_dir


def test_html_available_returns_false_when_not_installed() -> None:
    """
    Given: pytest-html is not importable
    When: _html_available is called
    Then: False is returned
    """
    with patch.dict(sys.modules, {"pytest_html": None}):
        result = _html_available()
    assert result is False


def test_steps_reporter_skips_empty_docstring() -> None:
    """
    Given: A test report with an empty docstring
    When: pytest_runtest_logreport is called
    Then: Nothing is written to the terminal
    """
    mock_config = MagicMock()
    mock_config.option.verbose = 1
    reporter = StepsReporter(mock_config)
    report = MagicMock(spec=pytest.TestReport)
    report.when = "call"
    report.skipped = False
    report.nodeid = "tests/features/my_feature/my_rule_test.py::test_something"
    report._beehave_docstring = ""
    reporter.pytest_runtest_logreport(report)
    mock_config.get_terminal_writer.assert_not_called()


def test_steps_reporter_falls_back_to_stdout(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """
    Given: A test report with a docstring and a broken terminal writer
    When: pytest_runtest_logreport is called
    Then: The docstring is written to stdout
    """
    mock_config = MagicMock()
    mock_config.option.verbose = 1
    mock_config.get_terminal_writer.side_effect = AttributeError("no writer")
    reporter = StepsReporter(mock_config)
    report = MagicMock(spec=pytest.TestReport)
    report.when = "call"
    report.skipped = False
    report.nodeid = "tests/features/my_feature/my_rule_test.py::test_something"
    report._beehave_docstring = "Given: a condition"
    reporter.pytest_runtest_logreport(report)
    captured = capsys.readouterr()
    assert "Given: a condition" in captured.out
