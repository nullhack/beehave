"""HTML Acceptance Criteria column plugin for pytest-beehave."""

from __future__ import annotations

import pytest


class HtmlStepsPlugin:
    """Adds an Acceptance Criteria column to pytest-html reports."""

    def pytest_html_results_table_header(self, cells: list[object]) -> None:
        """Insert the Acceptance Criteria column header.

        Args:
            cells: The list of header cells to modify.
        """
        cells.insert(2, "<th>Acceptance Criteria</th>")

    def pytest_html_results_table_row(
        self, report: pytest.TestReport, cells: list[object]
    ) -> None:
        """Insert the Acceptance Criteria column value for each row.

        Args:
            report: The test report for this row.
            cells: The list of row cells to modify.
        """
        nodeid = report.nodeid
        if "tests/features/" in nodeid:
            docstring = getattr(report, "_beehave_docstring", "") or ""
        else:
            docstring = ""
        cells.insert(2, f"<td style='white-space: pre-wrap;'>{docstring}</td>")
