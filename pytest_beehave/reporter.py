"""Terminal reporting for pytest-beehave actions."""

from __future__ import annotations

from typing import Protocol

from pytest_beehave.bootstrap import BootstrapResult


class TerminalWriterProtocol(Protocol):
    """Protocol for a terminal writer."""

    def line(self, text: str = "") -> None:  # pragma: no cover
        """Write a line to the terminal."""
        ...


def report_bootstrap(writer: TerminalWriterProtocol, result: BootstrapResult) -> None:
    """Report bootstrap actions to the terminal.

    Args:
        writer: Terminal writer to write to.
        result: The bootstrap result.
    """
    for name in result.created_subfolders:
        writer.line(f"[beehave] MKDIR {name}/")
    for path in result.migrated_files:
        writer.line(f"[beehave] MIGRATE {path}")
    for warning in result.collision_warnings:
        writer.line(f"[beehave] WARNING {warning}")


def report_id_write_back(writer: TerminalWriterProtocol, errors: list[str]) -> None:
    """Report ID write-back errors to the terminal.

    Args:
        writer: Terminal writer to write to.
        errors: List of error strings from assign_ids.
    """
    for error in errors:
        writer.line(f"[beehave] ERROR: {error}")


def report_sync_actions(writer: TerminalWriterProtocol, actions: list[str]) -> None:
    """Report sync actions to the terminal.

    Args:
        writer: Terminal writer to write to.
        actions: List of action description strings.
    """
    for action in actions:
        writer.line(f"[beehave] {action}")
