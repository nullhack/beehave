"""Unit tests for pytest_beehave.bootstrap module."""

from pathlib import Path

from pytest_beehave.bootstrap import BootstrapResult, bootstrap_features_directory


def test_bootstrap_result_is_noop_when_empty() -> None:
    """
    Given: A BootstrapResult with no changes
    When: is_noop is checked
    Then: Returns True
    """
    result = BootstrapResult(
        created_subfolders=(),
        migrated_files=(),
        collision_warnings=(),
    )
    assert result.is_noop is True


def test_bootstrap_result_is_not_noop_when_folders_created() -> None:
    """
    Given: A BootstrapResult with created subfolders
    When: is_noop is checked
    Then: Returns False
    """
    result = BootstrapResult(
        created_subfolders=("backlog",),
        migrated_files=(),
        collision_warnings=(),
    )
    assert result.is_noop is False


def test_bootstrap_returns_empty_result_when_root_does_not_exist(
    tmp_path: Path,
) -> None:
    """
    Given: A features root that does not exist
    When: bootstrap_features_directory is called
    Then: Returns a no-op BootstrapResult
    """
    missing = tmp_path / "nonexistent"
    result = bootstrap_features_directory(missing)
    assert result.is_noop is True
    assert result.created_subfolders == ()
    assert result.migrated_files == ()
    assert result.collision_warnings == ()


def test_bootstrap_migrates_loose_feature_files(tmp_path: Path) -> None:
    """
    Given: A features root with loose .feature files
    When: bootstrap_features_directory is called
    Then: Loose files are moved to backlog/
    """
    features_root = tmp_path / "features"
    features_root.mkdir()
    for subfolder in ("backlog", "in-progress", "completed"):
        (features_root / subfolder).mkdir()
    loose = features_root / "my-feature.feature"
    loose.write_text("Feature: My Feature\n", encoding="utf-8")

    result = bootstrap_features_directory(features_root)

    assert len(result.migrated_files) == 1
    assert result.migrated_files[0] == features_root / "backlog" / "my-feature.feature"
    assert not loose.exists()
    assert (features_root / "backlog" / "my-feature.feature").exists()


def test_bootstrap_warns_on_collision(tmp_path: Path) -> None:
    """
    Given: A loose .feature file that already exists in backlog/
    When: bootstrap_features_directory is called
    Then: A collision warning is added and file is not migrated
    """
    features_root = tmp_path / "features"
    features_root.mkdir()
    for subfolder in ("backlog", "in-progress", "completed"):
        (features_root / subfolder).mkdir()
    loose = features_root / "existing.feature"
    loose.write_text("Feature: Existing\n", encoding="utf-8")
    existing = features_root / "backlog" / "existing.feature"
    existing.write_text("Feature: Already there\n", encoding="utf-8")

    result = bootstrap_features_directory(features_root)

    assert len(result.collision_warnings) == 1
    assert "Cannot migrate" in result.collision_warnings[0]
    assert loose.exists()
    assert existing.read_text(encoding="utf-8") == "Feature: Already there\n"
