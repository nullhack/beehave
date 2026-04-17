"""ID assignment for pytest-beehave .feature files."""

import os
import re
import secrets
from pathlib import Path

FEATURE_STAGES: tuple[str, ...] = ("backlog", "in-progress", "completed")
_EXAMPLE_LINE_RE: re.Pattern[str] = re.compile(r"^(\s+)Example:", re.MULTILINE)
_ID_TAG_RE: re.Pattern[str] = re.compile(r"@id:[a-f0-9]{8}")


def _collect_existing_ids(content: str) -> set[str]:
    """Collect all @id hex values already present in file content.

    Args:
        content: Full text of a .feature file.

    Returns:
        Set of 8-char hex strings found in @id tags.
    """
    return set(re.findall(r"@id:([a-f0-9]{8})", content))


def _generate_unique_id(existing_ids: set[str]) -> str:
    """Generate a unique 8-char hex ID not already in existing_ids.

    Args:
        existing_ids: Set of IDs already used in the current file.

    Returns:
        A new unique 8-char hex string.
    """
    while True:
        candidate = secrets.token_hex(4)
        if candidate not in existing_ids:
            return candidate


def _insert_id_before_example(content: str, existing_ids: set[str]) -> str:
    """Insert @id tags before each untagged Example line.

    Args:
        content: Full text of a .feature file.
        existing_ids: Set of IDs already present in the file.

    Returns:
        Updated file content with @id tags inserted.
    """
    lines = content.splitlines(keepends=True)
    result: list[str] = []
    for line in lines:
        match = _EXAMPLE_LINE_RE.match(line)
        if match and not _id_tag_precedes(result):
            new_id = _generate_unique_id(existing_ids)
            existing_ids.add(new_id)
            indent = match.group(1)
            result.append(f"{indent}@id:{new_id}\n")
        result.append(line)
    return "".join(result)


def _id_tag_precedes(lines: list[str]) -> bool:
    """Check if the last non-empty line is an @id tag.

    Args:
        lines: Lines accumulated so far.

    Returns:
        True if the previous non-empty line contains an @id tag.
    """
    for line in reversed(lines):
        stripped = line.strip()
        if stripped:
            return bool(_ID_TAG_RE.search(stripped))
    return False


def _process_writable_file(feature_path: Path) -> None:
    """Insert @id tags into a writable .feature file for untagged Examples.

    Args:
        feature_path: Path to the .feature file to process.
    """
    content = feature_path.read_text(encoding="utf-8")
    existing_ids = _collect_existing_ids(content)
    updated = _insert_id_before_example(content, existing_ids)
    if updated != content:
        feature_path.write_text(updated, encoding="utf-8")


def _check_readonly_file(feature_path: Path) -> list[str]:
    """Collect error messages for untagged Examples in a read-only file.

    Args:
        feature_path: Path to the read-only .feature file.

    Returns:
        List of error strings, one per untagged Example.
    """
    errors: list[str] = []
    content = feature_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    for index, line in enumerate(lines):
        if not _EXAMPLE_LINE_RE.match(line):
            continue
        if not _id_tag_precedes(lines[:index]):
            title = line.strip().removeprefix("Example:").strip()
            errors.append(f"{feature_path}: Example '{title}' has no @id")
    return errors


def _process_feature_file(feature_path: Path) -> list[str]:
    """Process a single .feature file: write IDs or collect errors.

    Args:
        feature_path: Path to the .feature file.

    Returns:
        List of error strings (empty if writable or no untagged Examples).
    """
    if os.access(feature_path, os.W_OK):
        _process_writable_file(feature_path)
        return []
    return _check_readonly_file(feature_path)


def assign_ids(features_dir: Path) -> list[str]:
    """Assign @id tags to untagged Examples in all .feature files.

    For writable files, inserts @id tags in-place. For read-only files,
    returns error strings instead of modifying the file.

    Args:
        features_dir: Root directory containing backlog/, in-progress/,
            and completed/ subdirectories with .feature files.

    Returns:
        List of error strings for read-only files with missing @id tags.
        Empty list means all Examples are tagged or files are writable.
    """
    errors: list[str] = []
    for stage in FEATURE_STAGES:
        stage_dir = features_dir / stage
        if not stage_dir.exists():
            continue
        for feature_path in sorted(stage_dir.rglob("*.feature")):
            errors.extend(_process_feature_file(feature_path))
    return errors
