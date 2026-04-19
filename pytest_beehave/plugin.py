"""pytest plugin entry point for pytest-beehave."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from pytest_beehave.bootstrap import bootstrap_features_directory
from pytest_beehave.config import (
    is_explicitly_configured,
    resolve_features_path,
    show_steps_in_html,
    show_steps_in_terminal,
)
from pytest_beehave.hatch import run_hatch
from pytest_beehave.html_steps_plugin import HtmlStepsPlugin
from pytest_beehave.id_generator import assign_ids
from pytest_beehave.reporter import (
    report_bootstrap,
    report_id_write_back,
    report_sync_actions,
)
from pytest_beehave.steps_reporter import StepsReporter
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

    def line(self, text: str = "") -> None:
        """Write a line to the terminal.

        Args:
            text: The line to write.
        """
        try:
            config = self._config
            writer = config.get_terminal_writer()
            writer.line(text)
        except (AssertionError, AttributeError):
            sys.stdout.write(text + "\n")
            sys.stdout.flush()


def _exit_if_missing_configured_path(rootdir: Path, path: Path) -> None:
    """Exit pytest if features_path is explicitly configured but missing.

    Args:
        rootdir: Project root directory.
        path: Resolved features path.
    """
    if not path.exists() and is_explicitly_configured(rootdir):
        message = f"[beehave] features_path not found: {path}"
        sys.stderr.write(message + "\n")
        sys.stderr.flush()
        pytest.exit(message, returncode=1)


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


def _html_available() -> bool:
    """Return True if pytest-html is importable.

    Returns:
        True when pytest-html is installed.
    """
    return importlib.util.find_spec("pytest_html") is not None


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]) -> object:
    """Attach the test docstring to the report for steps display.

    Args:
        item: The test item being reported.
        call: The call info (unused).
    """
    outcome = yield
    report = outcome.get_result()
    test_object = getattr(item, "obj", None)
    report._beehave_docstring = (
        getattr(test_object, "__doc__", None) or "" if test_object is not None else ""
    )


def _register_output_plugins(config: pytest.Config, rootdir: Path) -> None:
    """Register terminal and HTML output plugins based on configuration.

    Args:
        config: The pytest Config object.
        rootdir: Project root directory.
    """
    pm = config.pluginmanager
    if show_steps_in_terminal(rootdir):
        pm.register(StepsReporter(config), "beehave-steps-reporter")
    if show_steps_in_html(rootdir) and _html_available():
        pm.register(HtmlStepsPlugin(), "beehave-html-steps")


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register --beehave-hatch and --beehave-hatch-force CLI options.

    Args:
        parser: The pytest argument parser.
    """
    group = parser.getgroup("beehave")
    group.addoption(
        "--beehave-hatch",
        action="store_true",
        default=False,
        help="Generate bee-themed example features directory and exit.",
    )
    group.addoption(
        "--beehave-hatch-force",
        action="store_true",
        default=False,
        help="Overwrite existing content when using --beehave-hatch.",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Read beehave configuration, bootstrap directory, sync stubs.

    Args:
        config: The pytest Config object (provides rootdir and stash).
    """
    rootdir = config.rootpath
    path = resolve_features_path(rootdir)
    if config.getoption("--beehave-hatch", default=False):
        force = bool(config.getoption("--beehave-hatch-force", default=False))
        try:
            written = run_hatch(path, force)
        except SystemExit as exc:
            pytest.exit(str(exc), returncode=1)
        writer = _PytestTerminalWriter(config)
        for entry in written:
            writer.line(f"[beehave] HATCH {entry}")
        pytest.exit("[beehave] hatch complete", returncode=0)
    _exit_if_missing_configured_path(rootdir, path)
    config.stash[features_path_key] = path
    if path.exists():
        _run_beehave_sync(config, path)
    _register_output_plugins(config, rootdir)
