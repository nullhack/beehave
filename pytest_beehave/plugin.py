"""pytest plugin entry point for pytest-beehave."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from pytest_beehave.bootstrap import bootstrap_features_directory
from pytest_beehave.config import is_explicitly_configured, resolve_features_path
from pytest_beehave.id_generator import assign_ids
from pytest_beehave.reporter import (
    report_bootstrap,
    report_id_write_back,
    report_sync_actions,
)
from pytest_beehave.sync_engine import run_sync

features_path_key: pytest.StashKey[Path] = pytest.StashKey()


class _PytestTerminalWriter:
    """Adapter wrapping pytest's terminal writer to match TerminalWriterProtocol."""

    def __init__(self, config: pytest.Config) -> None:
        """Initialise the adapter.

        Args:
            config: The pytest Config object.
        """
        self._config = config

    def line(self, s: str = "") -> None:
        """Write a line to the terminal.

        Args:
            s: The line to write.
        """
        try:
            config = self._config
            writer = config.get_terminal_writer()
            writer.line(s)
        except (AssertionError, AttributeError):
            sys.stdout.write(s + "\n")
            sys.stdout.flush()


def _exit_if_missing_configured_path(rootdir: Path, path: Path) -> None:
    """Exit pytest if features_path is explicitly configured but missing.

    Args:
        rootdir: Project root directory.
        path: Resolved features path.
    """
    if not path.exists() and is_explicitly_configured(rootdir):
        msg = f"[beehave] features_path not found: {path}"
        sys.stderr.write(msg + "\n")
        sys.stderr.flush()
        pytest.exit(msg, returncode=1)


def _run_beehave_sync(config: pytest.Config, path: Path) -> None:
    """Bootstrap, assign IDs, and sync stubs for the features directory.

    Args:
        config: The pytest Config object.
        path: The resolved features directory path.
    """
    writer = _PytestTerminalWriter(config)
    report_bootstrap(writer, bootstrap_features_directory(path))
    errors = assign_ids(path)
    report_id_write_back(writer, errors)
    if errors:
        pytest.exit("[beehave] untagged Examples in read-only files", returncode=1)
    report_sync_actions(writer, run_sync(path, config.rootpath / "tests" / "features"))


def pytest_configure(config: pytest.Config) -> None:
    """Read beehave configuration, bootstrap directory, sync stubs.

    Resolves the features directory from pyproject.toml. Bootstraps the
    canonical subfolder structure. Assigns IDs to untagged Examples. Syncs
    test stubs. Exits pytest with a hard error only when features_path is
    explicitly configured AND the path does not exist.

    Args:
        config: The pytest Config object (provides rootdir and stash).
    """
    rootdir = config.rootpath
    path = resolve_features_path(rootdir)
    _exit_if_missing_configured_path(rootdir, path)
    config.stash[features_path_key] = path
    if path.exists():
        _run_beehave_sync(config, path)
