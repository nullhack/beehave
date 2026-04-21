"""Tests for features dir bootstrap — feature file migration rule."""

from __future__ import annotations

from pathlib import Path

import pytest

from pytest_beehave.bootstrap import bootstrap_features_directory
from pytest_beehave.reporter import report_bootstrap


class TestFeatureFileMigration:
    """Tests for the Feature file migration Rule."""

    @pytest.mark.unit
    def test_feature_file_migration_e8b61d04(self, tmp_path: Path) -> None:
        """
        Given: the features directory contains a .feature file directly (not inside any subfolder)
        When: pytest is invoked
        Then: that .feature file exists in the backlog subfolder and no longer exists in the root features directory
        """
        features_root = tmp_path / "features"
        features_root.mkdir()
        for subfolder in ("backlog", "in-progress", "completed"):
            (features_root / subfolder).mkdir()
        loose = features_root / "my-feature.feature"
        loose.write_text("Feature: My Feature\n", encoding="utf-8")

        bootstrap_features_directory(features_root)

        assert not loose.exists()
        assert (features_root / "backlog" / "my-feature.feature").exists()

    @pytest.mark.unit
    def test_feature_file_migration_f3c97a52(self, tmp_path: Path) -> None:
        """
        Given: the features directory contains a non-.feature file (e.g. discovery.md) directly in the root
        When: pytest is invoked
        Then: that file remains in the root features directory and is not moved to backlog
        """
        features_root = tmp_path / "features"
        features_root.mkdir()
        for subfolder in ("backlog", "in-progress", "completed"):
            (features_root / subfolder).mkdir()
        non_feature = features_root / "discovery.md"
        non_feature.write_text("# Discovery\n", encoding="utf-8")

        bootstrap_features_directory(features_root)

        assert non_feature.exists()
        assert not (features_root / "backlog" / "discovery.md").exists()

    @pytest.mark.unit
    def test_feature_file_migration_a9d02b6e(self, tmp_path: Path) -> None:
        """
        Given: the features directory contains a .feature file inside the in-progress subfolder
        When: pytest is invoked
        Then: that file remains in the in-progress subfolder and is not moved to backlog
        """
        features_root = tmp_path / "features"
        features_root.mkdir()
        in_progress = features_root / "in-progress"
        in_progress.mkdir()
        (features_root / "backlog").mkdir()
        (features_root / "completed").mkdir()
        nested = in_progress / "my-feature" / "story.feature"
        nested.parent.mkdir(parents=True)
        nested.write_text("Feature: My Feature\n", encoding="utf-8")

        bootstrap_features_directory(features_root)

        assert nested.exists()
        assert not (features_root / "backlog" / "story.feature").exists()

    @pytest.mark.unit
    def test_feature_file_migration_d1e74c83(self, tmp_path: Path) -> None:
        """
        Given: the features directory contains a .feature file directly in the root
        When: pytest is invoked
        Then: the terminal output names the file that was moved to backlog
        """
        features_root = tmp_path / "features"
        features_root.mkdir()
        for subfolder in ("backlog", "in-progress", "completed"):
            (features_root / subfolder).mkdir()
        loose = features_root / "my-feature.feature"
        loose.write_text("Feature: My Feature\n", encoding="utf-8")

        result = bootstrap_features_directory(features_root)

        lines: list[str] = []

        class _Writer:
            def line(self, text: str = "") -> None:
                lines.append(text)

        report_bootstrap(_Writer(), result)
        assert any("my-feature.feature" in line for line in lines)
