"""Terminal steps reporter for pytest-beehave."""

from __future__ import annotations

import sys

import pytest


class StepsReporter:
    """Prints BDD step docstrings to the terminal for tests/features/ tests."""

    def __init__(self, config: pytest.Config) -> None:
        """Initialise the reporter.

        Args:
            config: The pytest Config object.
        """
        self._config = config

    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:
        """Print steps docstring after each test call phase report.

        Args:
            report: The test report for the current phase.
        """
        if report.when != "call" and not (report.when == "setup" and report.skipped):
            return
        config = self._config
        option = config.option
        verbose = option.verbose
        if verbose < 1:
            return
        nodeid = report.nodeid
        if "tests/features/" not in nodeid:
            return
        docstring = getattr(report, "_beehave_docstring", "")
        if not docstring:
            return
        self._write_steps(docstring.strip())

    def _write_steps(self, steps: str) -> None:
        """Write the steps string to the terminal or stdout fallback.

        Args:
            steps: The stripped docstring content to write.
        """
        try:
            config = self._config
            writer = config.get_terminal_writer()
            writer.write("\n" + steps + "\n")
        except (AssertionError, AttributeError):
            sys.stdout.write("\n" + steps + "\n")
            sys.stdout.flush()
