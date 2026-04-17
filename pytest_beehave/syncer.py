"""Stub sync logic for pytest-beehave."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from gherkin import Parser as GherkinParser

FEATURE_STAGES: tuple[str, ...] = ("backlog", "in-progress", "completed")
ID_TAG_RE: re.Pattern[str] = re.compile(r"@id:([a-f0-9]{8})")
ORPHAN_MARKER: str = (
    '@pytest.mark.skip(reason="orphan: no matching @id in .feature files")'
)
DEPRECATED_MARKER: str = "@pytest.mark.deprecated"
_DECORATOR_BLOCK_RE: re.Pattern[str] = re.compile(
    r"((?:@pytest\.mark\.\w+(?:\(.*?\))?\n)*)def test_\w+_([a-f0-9]{8})\b"
)


@dataclass(frozen=True, slots=True)
class _StepLine:
    """A single step line with keyword and text."""

    keyword: str
    text: str
    doc_string: str | None
    data_table: str | None


@dataclass(frozen=True, slots=True)
class _Example:
    """A single Example parsed from a .feature file."""

    id_hex: str
    steps: tuple[_StepLine, ...]
    background_sections: tuple[tuple[_StepLine, ...], ...]
    outline_examples: str | None
    deprecated: bool


def _slugify(name: str) -> str:
    """Convert a feature folder name to a Python-safe slug.

    Args:
        name: The feature folder name (kebab-case).

    Returns:
        Underscore-separated lowercase string.
    """
    return name.replace("-", "_").lower()


def _extract_id(tags: list[dict[str, Any]]) -> str | None:
    """Find the @id:<hex> value from a list of Gherkin AST tags.

    Args:
        tags: List of tag dicts from the Gherkin AST.

    Returns:
        The 8-char hex ID, or None if no @id tag is present.
    """
    for tag in tags:
        match = ID_TAG_RE.search(tag.get("name", ""))
        if match:
            return match.group(1)
    return None


def _compute_col_widths(all_cells: list[list[str]]) -> list[int]:
    """Compute the maximum width for each column across all rows.

    Args:
        all_cells: List of rows, each row is a list of cell value strings.

    Returns:
        List of column widths (one per column).
    """
    col_count = max(len(row) for row in all_cells)
    return [
        max(len(row[col]) for row in all_cells if col < len(row))
        for col in range(col_count)
    ]


def _render_padded_row(row_cells: list[str], col_widths: list[int]) -> str:
    """Render a single table row with padded cell values.

    Args:
        row_cells: Cell values for this row.
        col_widths: Maximum width for each column.

    Returns:
        Pipe-delimited row string.
    """
    padded = [
        row_cells[col].ljust(col_widths[col])
        if col < len(row_cells)
        else " " * col_widths[col]
        for col in range(len(col_widths))
    ]
    return "| " + " | ".join(padded) + " |"


def _render_data_table(rows: list[dict[str, Any]]) -> str:
    """Render a Gherkin data table preserving original column widths.

    Args:
        rows: List of row dicts, each with a 'cells' list of dicts with 'value'.

    Returns:
        Multi-line string with each row as '| val1 | val2 |'.
    """
    if not rows:
        return ""
    all_cells = [
        [cell.get("value", "") for cell in row.get("cells", [])] for row in rows
    ]
    col_widths = _compute_col_widths(all_cells)
    return "\n".join(_render_padded_row(row, col_widths) for row in all_cells)


def _extract_table_rows(examples_entry: dict[str, Any]) -> list[list[str]]:
    """Extract all rows (header + body) from an examples entry.

    Args:
        examples_entry: A single examples dict from the Gherkin AST.

    Returns:
        List of rows, each row is a list of cell value strings.
    """
    all_rows: list[list[str]] = []
    header = examples_entry.get("tableHeader")
    if header:
        all_rows.append([cell.get("value", "") for cell in header.get("cells", [])])
    for row in examples_entry.get("tableBody", []):
        all_rows.append([cell.get("value", "") for cell in row.get("cells", [])])
    return all_rows


def _render_examples_table(examples: list[dict[str, Any]]) -> str:
    """Render the Examples table from a Scenario Outline preserving column widths.

    Args:
        examples: List of examples dicts from the Gherkin AST.

    Returns:
        Rendered Examples table as a string.
    """
    if not examples:
        return ""
    all_rows = _extract_table_rows(examples[0])
    if not all_rows:
        return "Examples:"
    col_widths = _compute_col_widths(all_rows)
    lines = ["Examples:"] + [
        "  " + _render_padded_row(row, col_widths) for row in all_rows
    ]
    return "\n".join(lines)


def _build_step_line(step: dict[str, Any]) -> _StepLine:
    """Build a _StepLine from a Gherkin AST step dict.

    Args:
        step: A step dict from the Gherkin AST.

    Returns:
        A _StepLine with keyword, text, and optional doc_string/data_table.
    """
    keyword = step["keyword"].strip()
    text = step.get("text", "")
    doc_string: str | None = None
    data_table: str | None = None
    if "docString" in step:
        doc_string = step["docString"].get("content", "")
    if "dataTable" in step:
        data_table = _render_data_table(step["dataTable"].get("rows", []))
    return _StepLine(
        keyword=keyword, text=text, doc_string=doc_string, data_table=data_table
    )


def _build_steps(raw_steps: list[dict[str, Any]]) -> tuple[_StepLine, ...]:
    """Build a tuple of _StepLine from a list of Gherkin AST steps.

    Args:
        raw_steps: List of step dicts from the Gherkin AST.

    Returns:
        Tuple of _StepLine objects.
    """
    return tuple(_build_step_line(s) for s in raw_steps)


def _collect_background_steps(
    children: list[dict[str, Any]],
) -> tuple[_StepLine, ...] | None:
    """Extract background steps from a list of feature/rule children.

    Args:
        children: List of child dicts from the Gherkin AST.

    Returns:
        Tuple of _StepLine if a Background exists, else None.
    """
    for child in children:
        background = child.get("background")
        if background is not None:
            return _build_steps(background.get("steps", []))
    return None


def _build_background_sections(
    feature_background: tuple[_StepLine, ...] | None,
    rule_background: tuple[_StepLine, ...] | None,
) -> tuple[tuple[_StepLine, ...], ...]:
    """Build the background_sections tuple from feature and rule backgrounds.

    Args:
        feature_background: Feature-level background steps, or None.
        rule_background: Rule-level background steps, or None.

    Returns:
        Tuple of background step tuples (0, 1, or 2 entries).
    """
    sections: list[tuple[_StepLine, ...]] = []
    if feature_background is not None:
        sections.append(feature_background)
    if rule_background is not None:
        sections.append(rule_background)
    return tuple(sections)


def _extract_outline_examples(scenario: dict[str, Any]) -> str | None:
    """Extract the rendered Examples table from a Scenario Outline, if any.

    Args:
        scenario: Scenario dict from the Gherkin AST.

    Returns:
        Rendered Examples table string, or None if not a Scenario Outline.
    """
    raw = scenario.get("examples", [])
    return _render_examples_table(raw) if raw else None


def _is_deprecated(tags: list[dict[str, Any]]) -> bool:
    """Check if a scenario is tagged @deprecated.

    Args:
        tags: List of tag dicts from the Gherkin AST.

    Returns:
        True if any tag is @deprecated.
    """
    return any(t["name"] == "@deprecated" for t in tags)


def _make_example(
    id_hex: str,
    tags: list[dict[str, Any]],
    scenario: dict[str, Any],
    backgrounds: tuple[tuple[_StepLine, ...], ...],
) -> _Example:
    """Construct an _Example from pre-extracted parts.

    Args:
        id_hex: The 8-char hex ID.
        tags: Scenario tags list.
        scenario: Gherkin AST scenario dict.
        backgrounds: Pre-built background sections tuple.

    Returns:
        A fully constructed _Example.
    """
    return _Example(
        id_hex=id_hex,
        steps=_build_steps(scenario.get("steps", [])),
        background_sections=backgrounds,
        outline_examples=_extract_outline_examples(scenario),
        deprecated=_is_deprecated(tags),
    )


def _build_example(
    scenario: dict[str, Any],
    feature_background: tuple[_StepLine, ...] | None,
    rule_background: tuple[_StepLine, ...] | None,
) -> _Example | None:
    """Build an _Example from a scenario dict.

    Args:
        scenario: Gherkin AST scenario dict.
        feature_background: Feature-level background steps.
        rule_background: Rule-level background steps.

    Returns:
        _Example, or None if no @id tag.
    """
    tags = scenario.get("tags", [])
    id_hex = _extract_id(tags)
    if id_hex is None:
        return None
    backgrounds = _build_background_sections(feature_background, rule_background)
    return _make_example(id_hex, tags, scenario, backgrounds)


def _collect_scenario(
    scenario: dict[str, Any],
    feature_background: tuple[_StepLine, ...] | None,
    rule_background: tuple[_StepLine, ...] | None,
    examples: list[_Example],
) -> None:
    """Extract an _Example from a scenario dict and append to examples.

    Args:
        scenario: Scenario dict from the Gherkin AST.
        feature_background: Feature-level background steps, or None.
        rule_background: Rule-level background steps, or None.
        examples: List to append the _Example to.
    """
    example = _build_example(scenario, feature_background, rule_background)
    if example is not None:
        examples.append(example)


def _process_rule_children(
    rule: dict[str, Any],
    feature_background: tuple[_StepLine, ...] | None,
    examples: list[_Example],
) -> None:
    """Process all scenario children within a Rule block.

    Args:
        rule: Rule dict from the Gherkin AST.
        feature_background: Feature-level background steps, or None.
        examples: List to append _Example objects to.
    """
    rule_children = rule.get("children", [])
    rule_background = _collect_background_steps(rule_children)
    for rule_child in rule_children:
        scenario = rule_child.get("scenario")
        if scenario is not None:
            _collect_scenario(scenario, feature_background, rule_background, examples)


def _process_feature_child(
    child: dict[str, Any],
    feature_background: tuple[_StepLine, ...] | None,
    examples: list[_Example],
) -> None:
    """Process a single child of the feature (rule or scenario).

    Args:
        child: A child dict from the Gherkin AST feature children.
        feature_background: Feature-level background steps, or None.
        examples: List to append _Example objects to.
    """
    rule = child.get("rule")
    if rule is not None:
        _process_rule_children(rule, feature_background, examples)
        return
    scenario = child.get("scenario")
    if scenario is not None:
        _collect_scenario(scenario, feature_background, None, examples)


def _parse_examples(feature_path: Path) -> list[_Example]:
    """Parse all @id-tagged Examples from a .feature file.

    Args:
        feature_path: Path to the .feature file.

    Returns:
        List of parsed _Example objects (only those with @id tags).
    """
    text = feature_path.read_text(encoding="utf-8")
    doc = GherkinParser().parse(text)
    feature = cast(dict[str, Any] | None, doc.get("feature"))
    if not feature:
        return []
    feature_children = feature.get("children", [])
    feature_background = _collect_background_steps(feature_children)
    examples: list[_Example] = []
    for child in feature_children:
        _process_feature_child(child, feature_background, examples)
    return examples


def _render_step(step: _StepLine) -> str:
    """Render a single step line for inclusion in a docstring.

    Args:
        step: The step to render.

    Returns:
        Rendered step text, possibly with doc_string or data_table appended.
    """
    rendered = f"    {step.keyword}: {step.text}"
    if step.doc_string is not None:
        doc = step.doc_string
        indented = "\n".join(f"      {line}" for line in doc.splitlines())
        rendered = f"{rendered}\n{indented}"
    if step.data_table is not None:
        table = step.data_table
        indented = "\n".join(f"      {line}" for line in table.splitlines())
        rendered = f"{rendered}\n{indented}"
    return rendered


def _build_docstring(example: _Example) -> str:
    """Build the docstring body for a test stub.

    Args:
        example: The parsed example.

    Returns:
        Docstring content (without surrounding triple-quotes).
    """
    lines: list[str] = []
    for background_steps in example.background_sections:
        lines.append("    Background:")
        for step in background_steps:
            lines.append(_render_step(step))
    for step in example.steps:
        lines.append(_render_step(step))
    if example.outline_examples is not None:
        lines.append(f"    {example.outline_examples}")
    return "\n".join(lines)


def _build_decorator(example: _Example) -> str:
    """Build the decorator string for a test stub.

    Args:
        example: The parsed example.

    Returns:
        Decorator string (empty if not deprecated).
    """
    if example.deprecated:
        return f"{DEPRECATED_MARKER}\n"
    return ""


def _stub_text(feature_slug: str, example: _Example) -> str:
    """Generate a single test stub function as source text.

    Args:
        feature_slug: Underscored feature folder name.
        example: The parsed example.

    Returns:
        Complete test function source code as a string.
    """
    function_name = f"test_{feature_slug}_{example.id_hex}"
    body = _build_docstring(example)
    return (
        f"{_build_decorator(example)}"
        f"def {function_name}() -> None:\n"
        f'    """\n{body}\n    """\n'
        f"    raise NotImplementedError\n"
    )


def _build_file_header(story_slug: str) -> str:
    """Build the header for a new test stub file.

    Args:
        story_slug: The story file stem (underscore-separated).

    Returns:
        File header string including module docstring and imports.
    """
    title = story_slug.replace("_", " ")
    return f'"""Tests for {title} story."""\n\nimport pytest\n\n\n'


def _write_stub_file(test_file: Path, story_slug: str, content: str) -> None:
    """Write stub file content to disk, creating parent directories.

    Args:
        test_file: Path to the test file to create.
        story_slug: The story file stem (used for file header).
        content: The stub content to write (without header).
    """
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text(
        _build_file_header(story_slug) + content + "\n", encoding="utf-8"
    )


def _create_stub_file(
    feature_slug: str,
    story_slug: str,
    examples: list[_Example],
    test_file: Path,
) -> str:
    """Write a new test stub file for a .feature file.

    Args:
        feature_slug: Underscored feature folder name.
        story_slug: The story file stem (becomes test file name).
        examples: All examples from that .feature file.
        test_file: Path to the test file to create.

    Returns:
        Action description string.
    """
    stubs = "\n\n".join(_stub_text(feature_slug, ex) for ex in examples)
    _write_stub_file(test_file, story_slug, stubs)
    return f"CREATE {test_file} ({len(examples)} stubs)"


def _collect_new_stubs(
    examples: list[_Example],
    found_ids: set[str],
) -> list[_Example]:
    """Find examples that are not yet represented in the test file.

    Args:
        examples: All examples from the .feature file.
        found_ids: Set of @id hex values already found in the test file.

    Returns:
        List of examples that need new stubs appended.
    """
    return [ex for ex in examples if ex.id_hex not in found_ids]


def _apply_update_for_function(
    content: str,
    function_name: str,
    id_hex: str,
    feature_slug: str,
    examples_by_id: dict[str, _Example],
) -> str:
    """Apply update to a single function if its id_hex is in examples_by_id.

    Args:
        content: Full file content.
        function_name: The current function name.
        id_hex: The @id hex for this function.
        feature_slug: Underscored feature folder name.
        examples_by_id: Mapping of id_hex to _Example.

    Returns:
        Updated file content.
    """
    if id_hex not in examples_by_id:
        return content
    return _update_function_by_name(
        content, function_name, id_hex, feature_slug, examples_by_id[id_hex]
    )


def _apply_updates(
    content: str,
    feature_slug: str,
    examples_by_id: dict[str, _Example],
) -> tuple[str, set[str]]:
    """Apply docstring and rename updates to all matching functions.

    Args:
        content: Full file content.
        feature_slug: Underscored feature folder name.
        examples_by_id: Mapping of id_hex to _Example.

    Returns:
        Tuple of (updated_content, found_ids).
    """
    found_ids: set[str] = set()
    for name, id_hex in _top_level_test_functions(content):
        found_ids.add(id_hex)
        content = _apply_update_for_function(
            content, name, id_hex, feature_slug, examples_by_id
        )
    return content, found_ids


def _append_new_stubs(
    content: str, feature_slug: str, new_stubs: list[_Example]
) -> str:
    """Append new stub functions to existing file content.

    Args:
        content: Current file content.
        feature_slug: Underscored feature folder name.
        new_stubs: Examples that need new stubs appended.

    Returns:
        Updated file content with new stubs appended.
    """
    appended = "\n\n".join(_stub_text(feature_slug, ex) for ex in new_stubs)
    return content.rstrip("\n") + "\n\n\n" + appended + "\n"


def _transform_stub_content(
    content: str, feature_slug: str, examples: list[_Example]
) -> str:
    """Apply all updates (rename, docstring, new stubs) to file content.

    Args:
        content: Current file content.
        feature_slug: Underscored feature folder name.
        examples: All examples from the .feature file.

    Returns:
        Updated file content.
    """
    content, found_ids = _apply_updates(
        content, feature_slug, {ex.id_hex: ex for ex in examples}
    )
    new_stubs = _collect_new_stubs(examples, found_ids)
    if new_stubs:
        content = _append_new_stubs(content, feature_slug, new_stubs)
    return content


def _update_stub_file(
    feature_slug: str,
    examples: list[_Example],
    test_file: Path,
) -> str | None:
    """Update docstrings and rename functions in an existing test stub file.

    Args:
        feature_slug: Underscored feature folder name.
        examples: All examples from the .feature file.
        test_file: Path to the existing test file.

    Returns:
        Action string, or None if no changes were made.
    """
    original = test_file.read_text(encoding="utf-8")
    updated = _transform_stub_content(original, feature_slug, examples)
    if updated == original:
        return None
    test_file.write_text(updated, encoding="utf-8")
    return f"UPDATE {test_file}"


def _rename_function(content: str, old_name: str, new_name: str) -> str:
    """Rename a top-level test function in file content.

    Args:
        content: Full file content.
        old_name: The current function name.
        new_name: The new function name.

    Returns:
        Updated file content with the function renamed.
    """
    pattern = re.compile(
        rf"^def {re.escape(old_name)}\(([^)]*)\) -> None:",
        re.MULTILINE | re.DOTALL,
    )
    return pattern.sub(
        lambda m: f"def {new_name}({m.group(1)}) -> None:", content, count=1
    )


def _update_function_by_name(
    content: str,
    old_name: str,
    id_hex: str,
    feature_slug: str,
    example: _Example,
) -> str:
    """Rename and update docstring of one test function.

    Args:
        content: Full file content.
        old_name: Current function name.
        id_hex: The @id hex for this function.
        feature_slug: Current feature slug.
        example: Parsed example with updated steps.

    Returns:
        Updated file content.
    """
    new_name = f"test_{feature_slug}_{id_hex}"
    if old_name != new_name:
        content = _rename_function(content, old_name, new_name)
    return _replace_docstring(content, new_name, example)


def _build_func_def(function_name: str, params: str, example: _Example) -> str:
    """Build the replacement function definition with updated docstring.

    Args:
        function_name: The function name.
        params: The parameter list string.
        example: The example with updated steps.

    Returns:
        Replacement function definition string.
    """
    body = _build_docstring(example)
    return f'def {function_name}({params}) -> None:\n    """\n{body}\n    """\n'


def _replace_docstring(content: str, function_name: str, example: _Example) -> str:
    """Replace the docstring of a named function in the file content.

    Args:
        content: Full file content.
        function_name: The function name to find.
        example: The example with updated steps.

    Returns:
        Updated file content with replaced docstring.
    """
    pattern = re.compile(
        rf'def {re.escape(function_name)}\(([^)]*)\) -> None:\n    """(.*?)"""\n',
        re.DOTALL,
    )
    match = pattern.search(content)
    if not match:
        return content
    new_def = _build_func_def(function_name, match.group(1), example)
    return pattern.sub(new_def, content, count=1)


def _collect_ids_from_stage_dir(stage_dir: Path) -> set[str]:
    """Collect all @id hex values from all .feature files in a stage directory.

    Args:
        stage_dir: Path to a stage directory (backlog/, in-progress/, completed/).

    Returns:
        Set of 8-char hex IDs found in any .feature file under stage_dir.
    """
    ids: set[str] = set()
    for feature_file in stage_dir.rglob("*.feature"):
        text = feature_file.read_text(encoding="utf-8")
        ids.update(match.group(1) for match in ID_TAG_RE.finditer(text))
    return ids


def _collect_all_ids(features_dir: Path) -> frozenset[str]:
    """Collect all @id hex values from all .feature files across all stages.

    Args:
        features_dir: Root of the features directory.

    Returns:
        Frozenset of 8-char hex IDs found in any .feature file.
    """
    ids: set[str] = set()
    for stage in FEATURE_STAGES:
        stage_dir = features_dir / stage
        if stage_dir.exists():
            ids.update(_collect_ids_from_stage_dir(stage_dir))
    return frozenset(ids)


def _sync_orphans(tests_dir: Path, all_ids: frozenset[str]) -> list[str]:
    """Add or remove orphan skip markers for test functions.

    Args:
        tests_dir: Root of the tests/features/ directory.
        all_ids: All known @id hex values from .feature files.

    Returns:
        List of action description strings.
    """
    actions: list[str] = []
    for test_file in sorted(tests_dir.rglob("*_test.py")):
        content = test_file.read_text(encoding="utf-8")
        updated = _apply_orphan_markers(content, all_ids)
        if updated != content:
            test_file.write_text(updated, encoding="utf-8")
            actions.append(f"ORPHAN {test_file}")
    return actions


def _find_triple_quote_end(content: str, start: int, quote: str) -> int:
    r"""Find the end position of a triple-quoted string.

    Args:
        content: Full file content.
        start: Start position of the opening triple-quote.
        quote: The triple-quote delimiter ('\"\"\"' or \"'''\").

    Returns:
        Position after the closing triple-quote, or len(content) if not found.
    """
    end = content.find(quote, start + 3)
    if end == -1:
        return len(content)
    return end + 3


def _find_string_ranges(content: str) -> list[tuple[int, int]]:
    """Find the character ranges of all triple-quoted strings in content.

    Args:
        content: Full file content.

    Returns:
        List of (start, end) character index pairs for triple-quoted strings.
    """
    ranges: list[tuple[int, int]] = []
    pos = 0
    while pos < len(content):
        matched = _try_match_triple_quote(content, pos, ranges)
        pos = matched or pos + 1
    return ranges


def _try_match_triple_quote(
    content: str, pos: int, ranges: list[tuple[int, int]]
) -> int | None:
    """Try to match a triple-quoted string at pos; append range if found.

    Args:
        content: Full file content.
        pos: Current position to check.
        ranges: List to append (start, end) to if a match is found.

    Returns:
        New position after the string, or None if no match.
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
        pos: Character position to check.
        string_ranges: List of (start, end) ranges from _find_string_ranges.

    Returns:
        True if pos is inside any string range.
    """
    return any(start < pos < end for start, end in string_ranges)


def _top_level_test_functions(content: str) -> list[tuple[str, str]]:
    """Find top-level test function definitions, skipping those inside strings.

    Args:
        content: Full file content.

    Returns:
        List of (function_name, id_hex) tuples for top-level test functions.
    """
    string_ranges = _find_string_ranges(content)
    results: list[tuple[str, str]] = []
    for match in re.finditer(
        r"^def (test_[a-z0-9_]+_([a-f0-9]{8}))\(",
        content,
        re.MULTILINE,
    ):
        if not _in_string(match.start(), string_ranges):
            results.append((match.group(1), match.group(2)))
    return results


def _apply_orphan_markers(content: str, all_ids: frozenset[str]) -> str:
    """Apply or remove orphan markers in file content.

    Args:
        content: Full file content.
        all_ids: All known @id hex values.

    Returns:
        Updated file content.
    """
    for function_name, id_hex in _top_level_test_functions(content):
        if id_hex not in all_ids:
            content = _add_orphan_marker(content, function_name)
        else:
            content = _remove_orphan_marker(content, function_name)
    return content


def _insert_marker_before(content: str, pos: int) -> str:
    """Insert the orphan marker at pos if not already present there.

    Args:
        content: Full file content.
        pos: Character position of the def line start.

    Returns:
        Updated file content, unchanged if marker already present.
    """
    marker_line = f"{ORPHAN_MARKER}\n"
    if content[:pos].endswith(marker_line):
        return content
    return content[:pos] + marker_line + content[pos:]


def _add_orphan_marker(content: str, function_name: str) -> str:
    """Add orphan skip marker before a function if not already present.

    Args:
        content: Full file content.
        function_name: The function name to find.

    Returns:
        Updated file content.
    """
    match = re.search(
        rf"^def {re.escape(function_name)}\([^)]*\) -> None:",
        content,
        re.MULTILINE,
    )
    if not match:
        return content
    return _insert_marker_before(content, match.start())


def _remove_orphan_marker(content: str, function_name: str) -> str:
    """Remove orphan skip marker before a function if present.

    Args:
        content: Full file content.
        function_name: The function name to find.

    Returns:
        Updated file content.
    """
    escaped_marker = re.escape(ORPHAN_MARKER)
    escaped_name = re.escape(function_name)
    remove_pattern = re.compile(
        rf"^{escaped_marker}\n(def {escaped_name}\([^)]*\) -> None:)",
        re.MULTILINE | re.DOTALL,
    )
    return remove_pattern.sub(r"\1", content, count=1)


def _sync_folder(folder: Path, stage: str, tests_dir: Path) -> list[str]:
    """Sync stubs for all .feature files within one feature folder.

    Args:
        folder: Path to the feature folder (e.g., backlog/my-feature/).
        stage: Stage name (backlog, in-progress, completed).
        tests_dir: Root of the tests/features/ directory.

    Returns:
        List of action description strings.
    """
    actions: list[str] = []
    for feature_path in sorted(folder.glob("*.feature")):
        actions.extend(_sync_one_feature(feature_path, folder.name, stage, tests_dir))
    return actions


def _sync_stage(stage_dir: Path, stage: str, tests_dir: Path) -> list[str]:
    """Sync stubs for all feature folders within one stage directory.

    Args:
        stage_dir: Path to the stage directory (e.g., features_dir/backlog/).
        stage: Stage name (backlog, in-progress, completed).
        tests_dir: Root of the tests/features/ directory.

    Returns:
        List of action description strings.
    """
    actions: list[str] = []
    for folder in sorted(stage_dir.iterdir()):
        if not folder.is_dir():
            continue
        actions.extend(_sync_folder(folder, stage, tests_dir))
    return actions


def _sync_all_stages(features_dir: Path, tests_dir: Path) -> list[str]:
    """Sync stubs for all stages in the features directory.

    Args:
        features_dir: Root of the features directory.
        tests_dir: Root of the tests/features/ directory.

    Returns:
        List of action description strings.
    """
    actions: list[str] = []
    for stage in FEATURE_STAGES:
        stage_dir = features_dir / stage
        if stage_dir.exists():
            actions.extend(_sync_stage(stage_dir, stage, tests_dir))
    return actions


def sync_stubs(features_dir: Path, tests_dir: Path) -> list[str]:
    """Sync test stubs from .feature files to the tests directory.

    Scans features_dir for backlog/, in-progress/, and completed/ sub-folders.
    Creates or updates test stub files under tests_dir/<feature-name>/ for
    .feature files in backlog/ and in-progress/. Completed features are skipped.
    Orphan tests (no matching @id) receive a skip marker.

    Args:
        features_dir: Root of the features directory (contains backlog/,
            in-progress/, completed/).
        tests_dir: Root of the tests/features/ directory where stubs are written.

    Returns:
        List of action description strings. Empty list if nothing changed.
    """
    actions = _sync_all_stages(features_dir, tests_dir)
    all_ids = _collect_all_ids(features_dir)
    actions.extend(_sync_orphans(tests_dir, all_ids))
    return actions


def _resolve_test_file(
    folder_name: str,
    feature_path: Path,
    tests_dir: Path,
) -> tuple[str, str, Path]:
    """Resolve the feature slug, story slug, and test file path.

    Args:
        folder_name: The feature folder name (kebab-case).
        feature_path: Path to the .feature file.
        tests_dir: Root of the tests/features/ directory.

    Returns:
        Tuple of (feature_slug, story_slug, test_file_path).
    """
    feature_slug = _slugify(folder_name)
    story_slug = _slugify(feature_path.stem)
    test_file = tests_dir / feature_slug / f"{story_slug}_test.py"
    return feature_slug, story_slug, test_file


def _create_or_update_stub(
    feature_slug: str,
    story_slug: str,
    examples: list[_Example],
    test_file: Path,
) -> str | None:
    """Create a new stub file or update an existing one.

    Args:
        feature_slug: Underscored feature folder name.
        story_slug: The story file stem.
        examples: All examples from the .feature file.
        test_file: Path to the test file.

    Returns:
        Action description string, or None if no changes were made.
    """
    if not test_file.exists():
        return _create_stub_file(feature_slug, story_slug, examples, test_file)
    return _update_stub_file(feature_slug, examples, test_file)


def _toggle_deprecated_marker(content: str, id_hex: str, *, add: bool) -> str:
    """Add or remove @pytest.mark.deprecated before the test function for id_hex.

    Args:
        content: Full file content.
        id_hex: The 8-char hex ID of the test function to target.
        add: If True, add the marker; if False, remove it.

    Returns:
        Updated file content. Unchanged if the marker is already in the desired state.
    """
    marker_line = f"{DEPRECATED_MARKER}\n"
    for match in _DECORATOR_BLOCK_RE.finditer(content):
        if match.group(2) != id_hex:
            continue
        decorators = match.group(1)
        has_marker = marker_line in decorators
        if add and not has_marker:
            new_decorators = marker_line + decorators
            return (
                content[: match.start()]
                + new_decorators
                + content[match.start() + len(decorators) :]
            )
        if not add and has_marker:
            new_decorators = decorators.replace(marker_line, "")
            return (
                content[: match.start()]
                + new_decorators
                + content[match.start() + len(decorators) :]
            )
    return content


def _sync_deprecated_markers_in_file(
    examples: list[_Example], test_file: Path
) -> str | None:
    """Toggle @pytest.mark.deprecated for all examples in one test file.

    Args:
        examples: All examples from the .feature file.
        test_file: Path to the existing test file.

    Returns:
        Action string if the file was changed, else None.
    """
    if not test_file.exists():
        return None
    original = test_file.read_text(encoding="utf-8")
    content = original
    for example in examples:
        content = _toggle_deprecated_marker(
            content, example.id_hex, add=example.deprecated
        )
    if content == original:
        return None
    test_file.write_text(content, encoding="utf-8")
    return f"DEPRECATED {test_file}"


def _sync_active_feature(
    feature_path: Path, folder_name: str, tests_dir: Path
) -> list[str]:
    """Sync stubs for a non-completed .feature file.

    Args:
        feature_path: Path to the .feature file.
        folder_name: The feature folder name (kebab-case).
        tests_dir: Root of the tests/features/ directory.

    Returns:
        List of action description strings.
    """
    examples = _parse_examples(feature_path)
    if not examples:
        return []
    feature_slug, story_slug, test_file = _resolve_test_file(
        folder_name, feature_path, tests_dir
    )
    actions: list[str] = []
    stub_action = _create_or_update_stub(feature_slug, story_slug, examples, test_file)
    if stub_action:
        actions.append(stub_action)
    dep_action = _sync_deprecated_markers_in_file(examples, test_file)
    if dep_action:
        actions.append(dep_action)
    return actions


def _sync_completed_feature(
    feature_path: Path, folder_name: str, tests_dir: Path
) -> list[str]:
    """Sync deprecation markers only for a completed .feature file.

    Args:
        feature_path: Path to the .feature file.
        folder_name: The feature folder name (kebab-case).
        tests_dir: Root of the tests/features/ directory.

    Returns:
        List of action description strings.
    """
    examples = _parse_examples(feature_path)
    if not examples:
        return []
    _, _, test_file = _resolve_test_file(folder_name, feature_path, tests_dir)
    dep_action = _sync_deprecated_markers_in_file(examples, test_file)
    return [dep_action] if dep_action else []


def _sync_one_feature(
    feature_path: Path,
    folder_name: str,
    stage: str,
    tests_dir: Path,
) -> list[str]:
    """Sync stubs for a single .feature file.

    Args:
        feature_path: Path to the .feature file.
        folder_name: The feature folder name (kebab-case).
        stage: Feature stage (backlog, in-progress, completed).
        tests_dir: Root of the tests/features/ directory.

    Returns:
        List of action description strings.
    """
    if stage == "completed":
        return _sync_completed_feature(feature_path, folder_name, tests_dir)
    return _sync_active_feature(feature_path, folder_name, tests_dir)
