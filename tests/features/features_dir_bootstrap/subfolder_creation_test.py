"""Tests for features dir bootstrap — subfolder creation rule."""

from __future__ import annotations

from pathlib import Path

import pytest

from pytest_beehave.bootstrap import bootstrap_features_directory
from pytest_beehave.reporter import report_bootstrap


class TestSubfolderCreation:
    """Tests for the Subfolder creation Rule."""

    @pytest.mark.unit
    def test_subfolder_creation_3a1f8c2e(self, tmp_path: Path) -> None:
        """
        Given: the features directory exists with no backlog, in-progress, or completed subfolders
        When: pytest is invoked
        Then: the backlog, in-progress, and completed subfolders all exist inside the features directory
        """
        features_root = tmp_path / "features"
        features_root.mkdir()

        bootstrap_features_directory(features_root)

        assert (features_root / "backlog").is_dir()
        assert (features_root / "in-progress").is_dir()
        assert (features_root / "completed").is_dir()

    @pytest.mark.unit
    def test_subfolder_creation_b7d4e091(self, tmp_path: Path) -> None:
        """
        Given: the features directory exists with a backlog subfolder but no in-progress or completed subfolders
        When: pytest is invoked
        Then: the in-progress and completed subfolders are created and the backlog subfolder is unchanged
        """
        features_root = tmp_path / "features"
        features_root.mkdir()
        (features_root / "backlog").mkdir()
        sentinel = features_root / "backlog" / "my-feature.feature"
        sentinel.write_text("Feature: My Feature\n", encoding="utf-8")

        bootstrap_features_directory(features_root)

        assert (features_root / "in-progress").is_dir()
        assert (features_root / "completed").is_dir()
        assert sentinel.exists()
        assert sentinel.read_text(encoding="utf-8") == "Feature: My Feature\n"

    @pytest.mark.unit
    def test_subfolder_creation_c2a53f7d(self, tmp_path: Path) -> None:
        """
        Given: the features directory exists with no backlog, in-progress, or completed subfolders
        When: pytest is invoked
        Then: the terminal output names each subfolder that was created
        """
        features_root = tmp_path / "features"
        features_root.mkdir()

        result = bootstrap_features_directory(features_root)

        lines: list[str] = []

        class _Writer:
            def line(self, s: str = "") -> None:
                lines.append(s)

        report_bootstrap(_Writer(), result)
        assert any("backlog" in line for line in lines)
        assert any("in-progress" in line for line in lines)
        assert any("completed" in line for line in lines)
