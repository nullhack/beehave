"""Unit tests for pytest_beehave.reporter module."""

from pathlib import Path
from unittest.mock import MagicMock

from pytest_beehave.bootstrap import BootstrapResult
from pytest_beehave.reporter import (
    TerminalWriterProtocol,
    report_bootstrap,
    report_id_write_back,
    report_sync_actions,
)


def _make_writer() -> MagicMock:
    return MagicMock(spec=TerminalWriterProtocol)


def test_report_bootstrap_reports_created_subfolders() -> None:
    """
    Given: A BootstrapResult with created subfolders
    When: report_bootstrap is called
    Then: Writer.line is called for each created subfolder
    """
    writer = _make_writer()
    result = BootstrapResult(
        created_subfolders=("backlog", "in-progress"),
        migrated_files=(),
        collision_warnings=(),
    )
    report_bootstrap(writer, result)
    writer.line.assert_any_call("[beehave] MKDIR backlog/")
    writer.line.assert_any_call("[beehave] MKDIR in-progress/")


def test_report_bootstrap_reports_migrated_files() -> None:
    """
    Given: A BootstrapResult with migrated files
    When: report_bootstrap is called
    Then: Writer.line is called for each migrated file
    """
    writer = _make_writer()
    path = Path("/some/path/my-feature.feature")
    result = BootstrapResult(
        created_subfolders=(),
        migrated_files=(path,),
        collision_warnings=(),
    )
    report_bootstrap(writer, result)
    writer.line.assert_any_call(f"[beehave] MIGRATE {path}")


def test_report_bootstrap_reports_collision_warnings() -> None:
    """
    Given: A BootstrapResult with collision warnings
    When: report_bootstrap is called
    Then: Writer.line is called for each warning
    """
    writer = _make_writer()
    result = BootstrapResult(
        created_subfolders=(),
        migrated_files=(),
        collision_warnings=("Cannot migrate foo: bar exists",),
    )
    report_bootstrap(writer, result)
    writer.line.assert_any_call("[beehave] WARNING Cannot migrate foo: bar exists")


def test_report_bootstrap_does_nothing_for_noop() -> None:
    """
    Given: A no-op BootstrapResult
    When: report_bootstrap is called
    Then: Writer.line is never called
    """
    writer = _make_writer()
    result = BootstrapResult(
        created_subfolders=(),
        migrated_files=(),
        collision_warnings=(),
    )
    report_bootstrap(writer, result)
    writer.line.assert_not_called()


def test_report_id_write_back_reports_errors() -> None:
    """
    Given: A list of error strings
    When: report_id_write_back is called
    Then: Writer.line is called for each error
    """
    writer = _make_writer()
    report_id_write_back(writer, ["error one", "error two"])
    writer.line.assert_any_call("[beehave] ERROR: error one")
    writer.line.assert_any_call("[beehave] ERROR: error two")


def test_report_sync_actions_reports_actions() -> None:
    """
    Given: A list of action strings
    When: report_sync_actions is called
    Then: Writer.line is called for each action
    """
    writer = _make_writer()
    report_sync_actions(writer, ["CREATE /some/file", "UPDATE /other/file"])
    writer.line.assert_any_call("[beehave] CREATE /some/file")
    writer.line.assert_any_call("[beehave] UPDATE /other/file")
