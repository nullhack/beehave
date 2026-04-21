"""ID assignment for pytest-beehave .feature files."""

import itertools
import os
import re
import secrets
from collections.abc import Iterator
from pathlib import Path

FEATURE_STAGES: tuple[str, ...] = ("backlog", "in-progress", "completed")
_EXAMPLE_LINE_RE: re.Pattern[str] = re.compile(r"^(\s+)Example:", re.MULTILINE)
_ID_TAG_LINE_RE: re.Pattern[str] = re.compile(r"^\s*@id:\S+\s*$")


def _collect_existing_ids(content: str) -> set[str]:
    """Collect all @id values already present in file content, regardless of format.

    Captures every value after ``@id:`` up to the next whitespace so that
    non-standard tags (wrong length, non-hex characters) are included in the
    uniqueness set and never silently collide with newly generated IDs.

    Args:
        content: Full text of a .feature file.

    Returns:
        Set of all @id value strings found in the content.
    """
    return set(re.findall(r"@id:(\S+)", content))


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
    last_non_empty = next((ln for ln in reversed(lines) if ln.strip()), "")
    return bool(_ID_TAG_LINE_RE.match(last_non_empty))


def _is_id_tag_line(line: str) -> bool:
    """Return True if line is an @id tag line.

    Args:
        line: A single line from a .feature file.

    Returns:
        True if the line matches the @id tag pattern.
    """
    stripped = line.strip()
    return stripped.startswith("@") and bool(_ID_TAG_LINE_RE.match(line))


def _count_preceding_id_tags(lines: list[str]) -> int:
    """Count @id tags in the Gherkin tag block immediately before the current position.

    Scans backwards through lines, counting @id tag lines and skipping other
    tag lines and blanks, until a non-tag, non-blank line is found.

    Args:
        lines: Lines accumulated so far (or all lines before the current line).

    Returns:
        Number of @id tag lines in the preceding tag block.
    """
    count = 0
    for line in reversed(lines):
        stripped = line.strip()
        if not stripped:
            continue
        if not stripped.startswith("@"):
            break
        if _is_id_tag_line(line):
            count += 1
    return count


def _duplicate_id_error(
    feature_path: Path, line: str, preceding: list[str]
) -> str | None:
    """Return an error string if an Example line has two or more preceding @id tags.

    Args:
        feature_path: Path to the feature file (used in error message).
        line: The current line being processed.
        preceding: All lines before this one.

    Returns:
        Error string if duplicate @id tags are found, or None.
    """
    if not _EXAMPLE_LINE_RE.match(line):
        return None
    if _count_preceding_id_tags(preceding) < 2:
        return None
    stripped = line.strip()
    title = stripped.removeprefix("Example:").strip()
    return f"{feature_path}: Example '{title}' has duplicate @id tags"


def _duplicate_errors_in_content(feature_path: Path, content: str) -> list[str]:
    """Collect duplicate @id tag errors for all Examples in content.

    Args:
        feature_path: Path to the feature file (used in error messages).
        content: Full text of the .feature file.

    Returns:
        List of error strings for Examples with duplicate @id tags.
    """
    lines = content.splitlines()
    errors = [
        _duplicate_id_error(feature_path, line, lines[:index])
        for index, line in enumerate(lines)
    ]
    return [e for e in errors if e is not None]


def _process_writable_file(feature_path: Path) -> list[str]:
    """Insert @id tags into a writable .feature file for untagged Examples.

    Args:
        feature_path: Path to the .feature file to process.

    Returns:
        List of error strings if duplicate @id tags are found, else empty list.
    """
    content = feature_path.read_text(encoding="utf-8")
    errors = _duplicate_errors_in_content(feature_path, content)
    if errors:
        return errors
    existing_ids = _collect_existing_ids(content)
    updated = _insert_id_before_example(content, existing_ids)
    if updated != content:
        feature_path.write_text(updated, encoding="utf-8")
    return []


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
    stripped = line.strip()
    title = stripped.removeprefix("Example:").strip()
    return f"{feature_path}: Example '{title}' has no @id"


def _check_readonly_file(feature_path: Path) -> list[str]:
    """Collect error messages for untagged or duplicate-tagged Examples.

    Args:
        feature_path: Path to the read-only .feature file.

    Returns:
        List of error strings, one per problematic Example.
    """
    content = feature_path.read_text(encoding="utf-8")
    duplicate_errors = _duplicate_errors_in_content(feature_path, content)
    if duplicate_errors:
        return duplicate_errors
    lines = content.splitlines()
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
        List of error strings (empty if writable and no duplicates).
    """
    if os.access(feature_path, os.W_OK):
        return _process_writable_file(feature_path)
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
