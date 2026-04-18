"""Tests for features dir bootstrap — migration collision handling rule."""

from __future__ import annotations

from pathlib import Path

import pytest

from pytest_beehave.bootstrap import bootstrap_features_directory
from pytest_beehave.reporter import report_bootstrap


class TestMigrationCollisionHandling:
    """Tests for the Migration collision handling Rule."""

    @pytest.mark.unit
    def test_migration_collision_handling_7f2a0d51(self, tmp_path: Path) -> None:
        """
        Given: the features directory contains root-level feature.feature and backlog/feature.feature already exists
        When: pytest is invoked
        Then: root-level feature.feature is not moved and backlog/feature.feature is unchanged
        """
        features_root = tmp_path / "features"
        features_root.mkdir()
        for subfolder in ("backlog", "in-progress", "completed"):
            (features_root / subfolder).mkdir()
        root_file = features_root / "feature.feature"
        root_file.write_text("Feature: Root\n", encoding="utf-8")
        backlog_file = features_root / "backlog" / "feature.feature"
        backlog_file.write_text("Feature: Backlog\n", encoding="utf-8")

        bootstrap_features_directory(features_root)

        assert root_file.exists()
        assert root_file.read_text(encoding="utf-8") == "Feature: Root\n"
        assert backlog_file.read_text(encoding="utf-8") == "Feature: Backlog\n"

    @pytest.mark.unit
    def test_migration_collision_handling_8c3b1e96(self, tmp_path: Path) -> None:
        """
        Given: the features directory contains root-level feature.feature and backlog/feature.feature already exists
        When: pytest is invoked
        Then: the terminal output contains a warning naming the conflicting file and its location
        """
        features_root = tmp_path / "features"
        features_root.mkdir()
        for subfolder in ("backlog", "in-progress", "completed"):
            (features_root / subfolder).mkdir()
        root_file = features_root / "feature.feature"
        root_file.write_text("Feature: Root\n", encoding="utf-8")
        (features_root / "backlog" / "feature.feature").write_text(
            "Feature: Backlog\n", encoding="utf-8"
        )

        result = bootstrap_features_directory(features_root)

        lines: list[str] = []

        class _Writer:
            def line(self, s: str = "") -> None:
                lines.append(s)

        report_bootstrap(_Writer(), result)
        assert any("feature.feature" in line for line in lines)
        assert any("WARNING" in line or "Cannot migrate" in line for line in lines)
