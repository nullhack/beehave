"""Unit tests for id_generator module."""

from pathlib import Path

from pytest_beehave.id_generator import _check_readonly_file, _id_tag_precedes


def test_id_tag_precedes_returns_false_for_empty_lines() -> None:
    """_id_tag_precedes returns False when no preceding lines exist."""
    assert _id_tag_precedes([]) is False


def test_check_readonly_file_no_errors_when_examples_already_tagged(
    tmp_path: Path,
) -> None:
    """_check_readonly_file returns no errors for an already-tagged read-only file."""
    feature_file = tmp_path / "my.feature"
    feature_file.write_text(
        "Feature: F\n"
        "  @id:aabbccdd\n"
        "  Example: Already tagged\n"
        "    Given x\n"
        "    When y\n"
        "    Then z\n"
    )
    feature_file.chmod(0o444)
    assert _check_readonly_file(feature_file) == []
