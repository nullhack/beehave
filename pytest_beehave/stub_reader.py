"""Test stub reader for pytest-beehave."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from pytest_beehave.models import ExampleId, FeatureSlug

_ID_SUFFIX_RE: re.Pattern[str] = re.compile(r"test_\w+_([a-f0-9]{8})$")
_FUNC_RE: re.Pattern[str] = re.compile(
    r"^( {0,4})def (test_[a-z0-9_]+_([a-f0-9]{8}))\(",
    re.MULTILINE,
)
_CLASS_RE: re.Pattern[str] = re.compile(r"^class (Test\w+)", re.MULTILINE)


@dataclass(frozen=True, slots=True)
class ExistingStub:
    """Represents an existing test stub function found in a test file.

    Attributes:
        function_name: The full function name.
        example_id: The ExampleId extracted from the function name.
        feature_slug: The FeatureSlug inferred from the function name.
        class_name: The enclosing class name, or None for top-level.
        file_path: Path to the file containing this stub.
        markers: Tuple of decorator strings present on the function.
        docstring: The docstring body, or empty string.
    """

    function_name: str
    example_id: ExampleId
    feature_slug: FeatureSlug
    class_name: str | None
    file_path: Path
    markers: tuple[str, ...]
    docstring: str


def extract_example_id_from_name(name: str) -> ExampleId | None:
    """Extract the ExampleId from a test function name.

    Args:
        name: The test function name.

    Returns:
        ExampleId if found, else None.
    """
    match = _ID_SUFFIX_RE.search(name)
    if match:
        return ExampleId(match.group(1))
    return None


def _extract_feature_slug_from_name(name: str) -> FeatureSlug:
    """Extract the FeatureSlug from a test function name.

    Args:
        name: The test function name like 'test_my_feature_aabbccdd'.

    Returns:
        FeatureSlug for 'my_feature'.
    """
    # Strip 'test_' prefix and '_<8hex>' suffix
    without_prefix = name[len("test_") :]
    # remove '_aabbccdd' (9 chars: underscore + 8hex)
    without_suffix = without_prefix[:-9]
    return FeatureSlug(without_suffix)


def _find_triple_quote_end(content: str, start: int, quote: str) -> int:
    """Find the end position of a triple-quoted string.

    Args:
        content: Full file content.
        start: Start position of the opening triple-quote.
        quote: The triple-quote delimiter.

    Returns:
        Position after the closing triple-quote.
    """
    end = content.find(quote, start + 3)
    if end == -1:
        return len(content)
    return end + 3


def _find_string_ranges(content: str) -> list[tuple[int, int]]:
    """Find all triple-quoted string ranges in content.

    Args:
        content: Full file content.

    Returns:
        List of (start, end) ranges.
    """
    ranges: list[tuple[int, int]] = []
    pos = 0
    while pos < len(content):
        matched = _try_triple_quote(content, pos, ranges)
        pos = matched if matched is not None else pos + 1
    return ranges


def _try_triple_quote(
    content: str, pos: int, ranges: list[tuple[int, int]]
) -> int | None:
    """Try to match a triple-quoted string at pos.

    Args:
        content: Full file content.
        pos: Current position.
        ranges: List to append (start, end) to.

    Returns:
        New position after the string, or None.
    """
    for quote in ('"""', "'''"):
        if content[pos : pos + 3] == quote:
            end = _find_triple_quote_end(content, pos, quote)
            ranges.append((pos, end))
            return end
    return None


def _in_string(pos: int, string_ranges: list[tuple[int, int]]) -> bool:
    """Check if a position is inside a triple-quoted string.

    Args:
        pos: Character position.
        string_ranges: List of (start, end) ranges.

    Returns:
        True if pos is inside any string range.
    """
    return any(start < pos < end for start, end in string_ranges)


def _extract_docstring(content: str, func_start: int) -> str:
    """Extract the docstring body from a function at the given position.

    Args:
        content: Full file content.
        func_start: Start position of the def line.

    Returns:
        Docstring body string, or empty string.
    """
    # Find the first triple-quote after the def line
    def_end = content.find("\n", func_start)
    if def_end == -1:
        return ""
    after_def = content[def_end:]
    stripped = after_def.lstrip("\n")
    if not stripped.startswith('    """'):
        return ""
    open_pos = after_def.find('"""')
    close_pos = after_def.find('"""', open_pos + 3)
    if close_pos == -1:
        return ""
    return after_def[open_pos + 3 : close_pos]


def _is_decorator_line(stripped: str) -> bool:
    """Return True if a stripped line is a decorator.

    Args:
        stripped: A stripped source line.

    Returns:
        True if the line starts with '@'.
    """
    return stripped.startswith("@")


def _is_blank_or_comment(stripped: str) -> bool:
    """Return True if a stripped line is blank or a comment.

    Args:
        stripped: A stripped source line.

    Returns:
        True if the line is blank or starts with '#'.
    """
    return stripped == "" or stripped.startswith("#")


def _collect_markers_reversed(lines: list[str]) -> list[str]:
    """Collect decorator strings in reverse order from a list of source lines.

    Scans backwards, accumulating decorator lines until a non-decorator,
    non-blank, non-comment line is found.

    Args:
        lines: Source lines before a function definition.

    Returns:
        Decorator strings in reverse order (innermost first).
    """
    markers: list[str] = []
    for line in reversed(lines):
        stripped = line.strip()
        if _is_decorator_line(stripped):
            markers.append(stripped[1:])
            continue
        if not _is_blank_or_comment(stripped):
            break
    return markers


def _extract_markers(content: str, func_start: int) -> tuple[str, ...]:
    """Extract decorator strings before a function.

    Args:
        content: Full file content.
        func_start: Start position of the def line.

    Returns:
        Tuple of decorator strings (without @ prefix).
    """
    lines = content[:func_start].splitlines()
    return tuple(reversed(_collect_markers_reversed(lines)))


def _extract_class_name(content: str, func_start: int, indent: str) -> str | None:
    """Extract the enclosing class name for an indented method.

    Args:
        content: Full file content.
        func_start: Start position of the def line.
        indent: Leading whitespace of the def line.

    Returns:
        Class name string, or None for module-level functions.
    """
    if not indent:
        return None
    before = content[:func_start]
    class_matches = list(_CLASS_RE.finditer(before))
    if not class_matches:
        return None
    return class_matches[-1].group(1)


def _build_stub(
    content: str,
    match: re.Match[str],
    path: Path,
) -> ExistingStub:
    """Build an ExistingStub from a regex match in file content.

    Args:
        content: Full file content.
        match: Regex match for the function definition.
        path: Path to the file.

    Returns:
        ExistingStub for the matched function.
    """
    indent = match.group(1)
    func_name = match.group(2)
    example_id = ExampleId(match.group(3))
    return ExistingStub(
        function_name=func_name,
        example_id=example_id,
        feature_slug=_extract_feature_slug_from_name(func_name),
        class_name=_extract_class_name(content, match.start(), indent),
        file_path=path,
        markers=_extract_markers(content, match.start()),
        docstring=_extract_docstring(content, match.start()),
    )


def read_stubs_from_file(path: Path) -> list[ExistingStub]:
    """Read all test stub functions from a test file.

    Args:
        path: Path to the test file.

    Returns:
        List of ExistingStub objects found in the file.
    """
    if not path.exists():
        return []
    content = path.read_text(encoding="utf-8")
    string_ranges = _find_string_ranges(content)
    return [
        _build_stub(content, match, path)
        for match in _FUNC_RE.finditer(content)
        if not _in_string(match.start(), string_ranges)
    ]
