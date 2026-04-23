"""Nest command — bootstrap canonical directory structure."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

_CANONICAL_SUBFOLDERS: tuple[str, ...] = ("backlog", "in-progress", "completed")
_DEFAULT_FEATURES_DIR: str = "docs/features"
_TESTS_FEATURES_DIR: str = "tests/features"
_GITIGNORE_ENTRY: str = ".beehave_cache/"


@dataclass(frozen=True, slots=True)
class NestConfig:
    """Configuration for the nest command.

    Attributes:
        features_dir: Relative path to the features directory from project root.
        check: If True, verify structure without modifying anything.
        overwrite: If True, remove and recreate all managed directories.
    """

    features_dir: str
    check: bool
    overwrite: bool


@dataclass(frozen=True, slots=True)
class NestResult:
    """Result of running the nest command.

    Attributes:
        created_dirs: Paths of directories that were created.
        pyproject_modified: Whether pyproject.toml was modified.
        gitignore_modified: Whether .gitignore was modified.
        missing: Descriptions of missing items (populated in --check mode).
        warnings: Non-fatal warning messages.
    """

    created_dirs: tuple[Path, ...]
    pyproject_modified: bool
    gitignore_modified: bool
    missing: tuple[str, ...]
    warnings: tuple[str, ...]

    @property
    def is_noop(self) -> bool: ...

    @property
    def is_complete(self) -> bool: ...


def nest(project_root: Path, config: NestConfig) -> NestResult: ...
