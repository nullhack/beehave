"""Unit tests for id_generator module."""

from pathlib import Path

import pytest
from hypothesis import example, given
from hypothesis import strategies as st

from pytest_beehave.id_generator import (
    _check_readonly_file,
    _collect_existing_ids,
    _count_preceding_id_tags,
    _generate_unique_id,
    _id_tag_precedes,
)


def test_id_tag_precedes_returns_false_for_empty_lines() -> None:
    """_id_tag_precedes returns False when no preceding lines exist."""
    assert _id_tag_precedes([]) is False


def test_count_preceding_id_tags_skips_blank_lines() -> None:
    """_count_preceding_id_tags skips blank lines between tags and Example."""
    lines = ["  @id:aabbccdd\n", "\n", "  \n"]
    assert _count_preceding_id_tags(lines) == 1


def test_check_readonly_file_returns_error_for_duplicate_ids(
    tmp_path: Path,
) -> None:
    """_check_readonly_file returns an error when an Example has two @id tags."""
    feature_file = tmp_path / "my.feature"
    feature_file.write_text(
        "Feature: F\n"
        "  @id:aabbccdd\n"
        "  @id:11223344\n"
        "  Example: Duplicate IDs\n"
        "    Given x\n"
        "    When y\n"
        "    Then z\n"
    )
    feature_file.chmod(0o444)
    errors = _check_readonly_file(feature_file)
    assert len(errors) == 1
    assert "Duplicate IDs" in errors[0]


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


@pytest.mark.slow
@given(
    existing_tag=st.text(
        alphabet=st.characters(
            blacklist_categories=("Zs", "Cc", "Cf"),
            blacklist_characters="@: \t\n\r",
        ),
        min_size=1,
        max_size=32,
    )
)
@example(existing_tag="abcdef012")
@example(existing_tag="my-custom-name")
@example(existing_tag="aabbccdd")
def test_generate_unique_id_never_collides_with_existing_tag(
    existing_tag: str,
) -> None:
    """_generate_unique_id never returns a value whose first 8 chars match an existing tag.

    Property: for any string used as an existing @id value (regardless of length or
    format), _collect_existing_ids includes it in the uniqueness set and
    _generate_unique_id never returns a value that equals the first 8 chars of that tag.
    """
    content = f"  @id:{existing_tag}\n  Example: Something\n"
    existing_ids = _collect_existing_ids(content)
    assert existing_tag in existing_ids
    new_id = _generate_unique_id(existing_ids)
    assert new_id != existing_tag[:8]
