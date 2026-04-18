"""Tests for features dir bootstrap — no-op when structure is correct rule."""

from __future__ import annotations

from pathlib import Path

import pytest

from pytest_beehave.bootstrap import bootstrap_features_directory
from pytest_beehave.reporter import report_bootstrap


class TestNoOpWhenStructureIsCorrect:
    """Tests for the No-op when structure is correct Rule."""

    @pytest.mark.unit
    def test_no_op_when_structure_is_correct_5e6f9b17(self, tmp_path: Path) -> None:
        """
        Given: the features directory contains backlog, in-progress, and completed subfolders and no root-level .feature files
        When: pytest is invoked
        Then: the terminal output contains no bootstrap messages
        """
        features_root = tmp_path / "features"
        features_root.mkdir()
        for subfolder in ("backlog", "in-progress", "completed"):
            (features_root / subfolder).mkdir()

        result = bootstrap_features_directory(features_root)

        lines: list[str] = []

        class _Writer:
            def line(self, s: str = "") -> None:
                lines.append(s)

        report_bootstrap(_Writer(), result)
        assert lines == []

    @pytest.mark.unit
    def test_no_op_when_structure_is_correct_2d8a4c70(self, tmp_path: Path) -> None:
        """
        Given: the features directory does not exist
        When: pytest is invoked
        Then: pytest completes collection without errors and no bootstrap messages appear in the terminal
        """
        features_root = tmp_path / "features"
        # features_root does not exist

        result = bootstrap_features_directory(features_root)

        lines: list[str] = []

        class _Writer:
            def line(self, s: str = "") -> None:
                lines.append(s)

        report_bootstrap(_Writer(), result)
        assert result.is_noop
        assert lines == []
