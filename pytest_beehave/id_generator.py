"""ID assignment for pytest-beehave .feature files."""

import itertools
import os
import re
import secrets
from collections.abc import Iterator
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


def _candidate_stream() -> Iterator[str]:
    """Yield an infinite stream of random 8-char hex candidates.

    Yields:
        Random 8-char hex strings.
    """
    while True:
        yield secrets.token_hex(4)


def _generate_unique_id(existing_ids: set[str]) -> str:
    """Generate a unique 8-char hex ID not already in existing_ids.

    Args:
        existing_ids: Set of IDs already used in the current file.

    Returns:
        A new unique 8-char hex string.
    """
    return next(c for c in _candidate_stream() if c not in existing_ids)


def _prepend_id_tag(line: str, result: list[str], existing_ids: set[str]) -> None:
    """Prepend an @id tag line before an Example line if not already tagged.

    Mutates result and existing_ids in-place.

    Args:
        line: The current line being processed.
        result: Accumulated output lines so far.
        existing_ids: Set of IDs already used (mutated when a new ID is added).
    """
    match = _EXAMPLE_LINE_RE.match(line)
    if match is None:
        return
    if _id_tag_precedes(result):
        return
    new_id = _generate_unique_id(existing_ids)
    existing_ids.add(new_id)
    indent = match.group(1)
    result.append(f"{indent}@id:{new_id}\n")


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
        _prepend_id_tag(line, result, existing_ids)
        result.append(line)
    return "".join(result)


def _id_tag_precedes(lines: list[str]) -> bool:
    """Check if the last non-empty line is an @id tag.

    Args:
        lines: Lines accumulated so far.

    Returns:
        True if the previous non-empty line contains an @id tag.
    """
    last_non_empty = next((ln.strip() for ln in reversed(lines) if ln.strip()), "")
    return bool(_ID_TAG_RE.search(last_non_empty))


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


def _missing_id_error(
    feature_path: Path, line: str, preceding: list[str]
) -> str | None:
    """Return an error string if this Example line has no preceding @id tag.

    Args:
        feature_path: Path to the feature file (used in error message).
        line: The current line from the feature file.
        preceding: All lines before this one.

    Returns:
        Error string if an @id tag is missing, or None.
    """
    if not _EXAMPLE_LINE_RE.match(line):
        return None
    if _id_tag_precedes(preceding):
        return None
    title = line.strip().removeprefix("Example:").strip()
    return f"{feature_path}: Example '{title}' has no @id"


def _check_readonly_file(feature_path: Path) -> list[str]:
    """Collect error messages for untagged Examples in a read-only file.

    Args:
        feature_path: Path to the read-only .feature file.

    Returns:
        List of error strings, one per untagged Example.
    """
    lines = feature_path.read_text(encoding="utf-8").splitlines()
    errors = [
        _missing_id_error(feature_path, line, lines[:index])
        for index, line in enumerate(lines)
    ]
    return [e for e in errors if e is not None]


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


def _process_stage(features_dir: Path, stage: str) -> list[str]:
    """Process all .feature files in a single stage directory.

    Args:
        features_dir: Root features directory.
        stage: Stage subdirectory name (e.g. "in-progress").

    Returns:
        List of error strings from read-only files with missing @id tags.
    """
    stage_dir = features_dir / stage
    if not stage_dir.exists():
        return []
    return list(
        itertools.chain.from_iterable(
            _process_feature_file(p) for p in sorted(stage_dir.rglob("*.feature"))
        )
    )


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
    return list(
        itertools.chain.from_iterable(
            _process_stage(features_dir, stage) for stage in FEATURE_STAGES
        )
    )
