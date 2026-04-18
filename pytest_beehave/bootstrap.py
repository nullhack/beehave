"""Bootstrap logic for the features directory structure."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

_CANONICAL_SUBFOLDERS: tuple[str, ...] = ("backlog", "in-progress", "completed")


@dataclass(frozen=True, slots=True)
class BootstrapResult:
    """Result of bootstrapping the features directory.

    Attributes:
        created_subfolders: Names of subfolders that were created.
        migrated_files: Paths of files that were migrated.
        collision_warnings: Warning messages for name collisions.
    """

    created_subfolders: tuple[str, ...]
    migrated_files: tuple[Path, ...]
    collision_warnings: tuple[str, ...]

    @property
    def is_noop(self) -> bool:
        """Return True if bootstrap made no changes."""
        return (
            len(self.created_subfolders) == 0
            and len(self.migrated_files) == 0
            and len(self.collision_warnings) == 0
        )


def _ensure_canonical_subfolders(features_root: Path) -> tuple[str, ...]:
    """Create missing canonical subfolders under features_root.

    Args:
        features_root: The features root directory.

    Returns:
        Tuple of subfolder names that were created.
    """
    created: list[str] = []
    for name in _CANONICAL_SUBFOLDERS:
        subfolder = features_root / name
        if not subfolder.exists():
            subfolder.mkdir(parents=True, exist_ok=True)
            created.append(name)
    return tuple(created)


def _migrate_loose_feature_files(
    features_root: Path,
) -> tuple[tuple[Path, ...], tuple[str, ...]]:
    """Move any loose .feature files in features_root into backlog/.

    Files that collide with an existing path in backlog/ are skipped
    with a warning.

    Args:
        features_root: The features root directory.

    Returns:
        Tuple of (migrated_paths, warning_strings).
    """
    migrated: list[Path] = []
    warnings: list[str] = []
    backlog_dir = features_root / "backlog"
    for item in sorted(features_root.iterdir()):
        if item.is_dir() or item.suffix != ".feature":
            continue
        target = backlog_dir / item.name
        if target.exists():
            warnings.append(f"Cannot migrate {item}: {target} already exists")
            continue
        item.rename(target)
        migrated.append(target)
    return tuple(migrated), tuple(warnings)


def bootstrap_features_directory(features_root: Path) -> BootstrapResult:
    """Ensure the features directory has the canonical subfolder structure.

    Creates backlog/, in-progress/, and completed/ if missing. Migrates
    any loose .feature files at the root level into backlog/.

    Args:
        features_root: Root of the features directory.

    Returns:
        BootstrapResult describing what was done.
    """
    if not features_root.exists():
        return BootstrapResult(
            created_subfolders=(),
            migrated_files=(),
            collision_warnings=(),
        )
    created = _ensure_canonical_subfolders(features_root)
    migrated, warnings = _migrate_loose_feature_files(features_root)
    return BootstrapResult(
        created_subfolders=created,
        migrated_files=migrated,
        collision_warnings=warnings,
    )
