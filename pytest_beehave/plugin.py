"""pytest plugin entry point for pytest-beehave."""

from pathlib import Path

import pytest

from pytest_beehave.config import is_explicitly_configured, resolve_features_path
from pytest_beehave.id_generator import assign_ids
from pytest_beehave.syncer import sync_stubs

features_path_key: pytest.StashKey[Path] = pytest.StashKey()


def pytest_configure(config: pytest.Config) -> None:
    """Read beehave configuration and store the resolved features path.

    Resolves the features directory from pyproject.toml. Exits pytest with a
    hard error only when features_path is explicitly configured AND the path
    does not exist. When using the default path, stashes it regardless of
    existence so pytest_sessionstart can handle the absent-directory case.

    Args:
        config: The pytest Config object (provides rootdir and stash).
    """
    rootdir = config.rootpath
    path = resolve_features_path(rootdir)
    if not path.exists() and is_explicitly_configured(rootdir):
        pytest.exit(
            f"[beehave] features_path not found: {path}",
            returncode=1,
        )
    config.stash[features_path_key] = path


def _report_lines(config: pytest.Config, lines: list[str], prefix: str) -> None:
    """Write a list of lines to the terminal writer with a prefix.

    Args:
        config: The pytest Config object.
        lines: Lines to write.
        prefix: Prefix string for each line.
    """
    writer = config.get_terminal_writer()
    for line in lines:
        writer.line(f"{prefix}{line}")


def pytest_sessionstart(session: pytest.Session) -> None:
    """Run ID assignment and stub sync before test collection begins.

    Reads the stashed features path, assigns IDs to untagged Examples,
    syncs test stubs, and reports actions to the terminal. Exits with
    a non-zero code if read-only files have untagged Examples. Skips
    silently if the features directory is absent.

    Args:
        session: The pytest Session object.
    """
    config = session.config
    features_dir = config.stash[features_path_key]
    if not features_dir.exists():
        return
    errors = assign_ids(features_dir)
    if errors:
        _report_lines(config, errors, "[beehave] ERROR: ")
        pytest.exit("[beehave] untagged Examples in read-only files", returncode=1)
    tests_dir = config.rootpath / "tests" / "features"
    actions = sync_stubs(features_dir, tests_dir)
    _report_lines(config, actions, "[beehave] ")
