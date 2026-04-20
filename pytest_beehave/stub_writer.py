"""Test stub writer for pytest-beehave."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from pytest_beehave.config import StubFormat
from pytest_beehave.feature_parser import (
    ParsedExample,
    ParsedFeature,
    ParsedRule,
    ParsedStep,
)
from pytest_beehave.models import ExampleId, FeatureSlug, RuleSlug

_DECORATOR_RE: re.Pattern[str] = re.compile(
    r"^( *)((?:@pytest\.mark\.\w+(?:\(.*?\))?\n\1)*)def test_\w+_([a-f0-9]{8})\b",
    re.MULTILINE,
)
_ORPHAN_MARKER_LINE = (
    '@pytest.mark.skip(reason="orphan: no matching @id in .feature files")\n'
)


@dataclass(frozen=True, slots=True)
class SyncAction:
    """Description of a stub sync action taken.

    Attributes:
        action: The action type (CREATE, UPDATE, ORPHAN, DEPRECATED).
        path: Path to the affected test file.
        detail: Optional extra detail string.
    """

    action: str
    path: Path
    detail: str = ""

    def __str__(self) -> str:
        """Return a human-readable summary of the action."""
        if self.detail:
            return f"{self.action} {self.path} ({self.detail})"
        return f"{self.action} {self.path}"


@dataclass(frozen=True, slots=True)
class StubSpec:
    """Specification for a single test stub to write.

    Attributes:
        feature_slug: The feature slug (underscored).
        rule_slug: The rule slug (underscore-separated), or None for top-level stubs.
        example: The parsed example.
        feature: The full parsed feature (for docstring context).
        stub_format: The output format for the stub ("functions" or "classes").
    """

    feature_slug: FeatureSlug
    rule_slug: RuleSlug | None
    example: ParsedExample
    feature: ParsedFeature
    stub_format: StubFormat = "functions"


def build_function_name(feature_slug: FeatureSlug, example_id: ExampleId) -> str:
    """Build the test function name from slug and ID.

    Args:
        feature_slug: The feature slug.
        example_id: The example ID.

    Returns:
        String like 'test_my_feature_aabbccdd'.
    """
    return f"test_{feature_slug}_{example_id}"


def build_class_name(rule_slug: RuleSlug) -> str:
    """Build the test class name from a rule slug.

    Args:
        rule_slug: The rule slug (underscore-separated).

    Returns:
        String like 'TestMyRule'.
    """
    parts = str(rule_slug).split("_")
    return "Test" + "".join(p.capitalize() for p in parts if p)


def _render_step(step: ParsedStep) -> str:
    """Render a single step for a docstring.

    Args:
        step: The step to render.

    Returns:
        Rendered step text with optional doc_string/data_table.
    """
    rendered = f"    {step.keyword}: {step.text}"
    if step.doc_string is not None:
        lines = step.doc_string.splitlines()
        rendered = f"{rendered}\n" + "\n".join(f"      {ln}" for ln in lines)
    if step.data_table is not None:
        lines = step.data_table.splitlines()
        rendered = f"{rendered}\n" + "\n".join(f"      {ln}" for ln in lines)
    return rendered


def _render_background_section(steps: tuple[ParsedStep, ...]) -> list[str]:
    """Render a single background section as docstring lines.

    Args:
        steps: The background steps.

    Returns:
        List of rendered lines.
    """
    lines = ["    Background:"]
    lines.extend(_render_step(step) for step in steps)
    return lines


def build_docstring(
    feature: ParsedFeature,
    rule: ParsedRule | None,
    example: ParsedExample,
) -> str:
    """Build the docstring body for a test stub.

    Args:
        feature: The parsed feature (not used directly, kept for interface).
        rule: The parsed rule containing this example, or None.
        example: The parsed example.

    Returns:
        Docstring content (without surrounding triple-quotes).
    """
    lines: list[str] = []
    for bg_steps in example.background_sections:
        lines.extend(_render_background_section(bg_steps))
    if example.background_sections and example.steps:
        lines.append("")
    lines.extend(_render_step(step) for step in example.steps)
    if example.outline_examples is not None:
        lines.append(f"    {example.outline_examples}")
    return "\n".join(lines)


def _stub_decorator(is_deprecated: bool) -> str:
    """Return the decorator line for a new stub.

    Args:
        is_deprecated: If True, return deprecated marker; else skip marker.

    Returns:
        Decorator line string.
    """
    if is_deprecated:
        return "@pytest.mark.deprecated\n"
    return '@pytest.mark.skip(reason="not yet implemented")\n'


def _stub_function_source(
    function_name: str,
    docstring_body: str,
    is_deprecated: bool,
    *,
    is_method: bool = False,
) -> str:
    """Build full source text for a single test stub function.

    Args:
        function_name: The test function name.
        docstring_body: The docstring body (without triple-quotes).
        is_deprecated: If True, add @pytest.mark.deprecated.
        is_method: If True, emit (self) as the parameter.

    Returns:
        Full function source as a string.
    """
    decorator = _stub_decorator(is_deprecated)
    params = "self" if is_method else ""
    return (
        f"{decorator}"
        f"def {function_name}({params}) -> None:\n"
        f'    """\n{docstring_body}\n    """\n'
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


def _indent_stub(source: str, indent: str = "    ") -> str:
    """Indent all lines of a stub by the given prefix.

    Args:
        source: The stub source code.
        indent: Indentation prefix.

    Returns:
        Indented source.
    """
    return "\n".join(
        indent + line if line.strip() else line for line in source.splitlines()
    )


def _append_stub_to_file(path: Path, function_source: str) -> None:
    """Append a stub function to an existing file.

    Args:
        path: Path to the test file.
        function_source: The stub function source code.
    """
    existing = path.read_text(encoding="utf-8")
    updated = existing.rstrip("\n") + "\n\n\n" + function_source + "\n"
    path.write_text(updated, encoding="utf-8")


def _write_top_level_stub(path: Path, function_source: str) -> SyncAction:
    """Write a top-level (no Rule) stub to file.

    Args:
        path: Path to the test file.
        function_source: Full function source code.

    Returns:
        SyncAction describing what was done.
    """
    if not path.exists():
        stem = path.stem
        story_slug = stem.removesuffix("_test")
        parent = path.parent
        parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            _build_file_header(story_slug) + function_source + "\n",
            encoding="utf-8",
        )
        return SyncAction(action="CREATE", path=path)
    _append_stub_to_file(path, function_source)
    return SyncAction(action="UPDATE", path=path)


def write_stub_to_file(path: Path, spec: StubSpec) -> SyncAction:
    """Write a test stub for a single example to a test file.

    Creates the file if it doesn't exist, appends if it does.

    Args:
        path: Path to the test file.
        spec: The stub specification.

    Returns:
        A SyncAction describing what was done.
    """
    example = spec.example
    function_name = build_function_name(spec.feature_slug, example.example_id)
    rule = _find_rule(spec.feature, spec.rule_slug) if spec.rule_slug else None
    docstring_body = build_docstring(spec.feature, rule, example)
    is_class_method = spec.rule_slug is not None and spec.stub_format == "classes"
    function_source = _stub_function_source(
        function_name, docstring_body, example.is_deprecated, is_method=is_class_method
    )
    if is_class_method:
        return _write_class_based_stub(path, spec, function_name, function_source)
    return _write_top_level_stub(path, function_source)


def _create_class_file(path: Path, class_name: str, method_source: str) -> None:
    """Create a new test file with a class containing a method stub.

    Args:
        path: Path to create.
        class_name: The test class name.
        method_source: Indented method source.
    """
    stem = path.stem
    story_slug = stem.removesuffix("_test")
    parent = path.parent
    parent.mkdir(parents=True, exist_ok=True)
    class_block = f"class {class_name}:\n{method_source}\n"
    path.write_text(
        _build_file_header(story_slug) + class_block + "\n", encoding="utf-8"
    )


def _append_to_class_file(path: Path, class_name: str, method_source: str) -> None:
    """Append a method stub to an existing test file with a class.

    Args:
        path: Path to the test file.
        class_name: The test class name.
        method_source: Indented method source.
    """
    content = path.read_text(encoding="utf-8")
    if f"class {class_name}:" not in content:
        class_block = f"class {class_name}:\n{method_source}\n"
        updated = content.rstrip("\n") + "\n\n\n" + class_block + "\n"
    else:
        updated = content.rstrip("\n") + "\n\n" + method_source + "\n"
    path.write_text(updated, encoding="utf-8")


def _write_class_based_stub(
    path: Path,
    spec: StubSpec,
    function_name: str,
    function_source: str,
) -> SyncAction:
    """Write a class-method stub for a Rule-based spec.

    Args:
        path: Path to the test file.
        spec: The stub specification.
        function_name: The test function name.
        function_source: The function source code (module-level style).

    Returns:
        SyncAction describing the action taken.
    """
    if spec.rule_slug is None:
        raise ValueError("rule_slug must not be None for class-based stubs")
    class_name = build_class_name(spec.rule_slug)
    method_source = _indent_stub(function_source)
    if not path.exists():
        _create_class_file(path, class_name, method_source)
        return SyncAction(action="CREATE", path=path)
    _append_to_class_file(path, class_name, method_source)
    return SyncAction(action="UPDATE", path=path)


def _find_rule(feature: ParsedFeature, rule_slug: RuleSlug) -> ParsedRule | None:
    """Find a rule in a feature by its slug.

    Args:
        feature: The parsed feature.
        rule_slug: The rule slug to find.

    Returns:
        The matching ParsedRule, or None.
    """
    for rule in feature.rules:
        if rule.rule_slug == rule_slug:
            return rule
    return None


def _docstring_pattern(function_name: str) -> re.Pattern[str]:
    """Build a compiled docstring-replacement regex for a named function.

    Args:
        function_name: The test function name.

    Returns:
        Compiled regex pattern matching def line + docstring.
    """
    return re.compile(
        rf'(def {re.escape(function_name)}\([^)]*\) -> None:\n    """).*?(""")',
        re.DOTALL,
    )


def _update_docstring_in_content(
    content: str,
    function_name: str,
    new_docstring_body: str,
) -> str:
    """Replace the docstring of a named function in file content.

    Args:
        content: Full file content.
        function_name: The function name to find.
        new_docstring_body: New docstring body (without triple-quotes).

    Returns:
        Updated file content.
    """
    pattern = _docstring_pattern(function_name)
    replace_with = new_docstring_body

    def replacer(m: re.Match[str]) -> str:
        return f"{m.group(1)}\n{replace_with}\n    {m.group(2)}"

    return pattern.sub(replacer, content, count=1)


def _rename_function_in_content(content: str, old_name: str, new_name: str) -> str:
    """Rename a test function in file content.

    Args:
        content: Full file content.
        old_name: Current function name.
        new_name: New function name.

    Returns:
        Updated file content.
    """
    pattern = re.compile(
        rf"^def {re.escape(old_name)}\(([^)]*)\) -> None:",
        re.MULTILINE,
    )
    return pattern.sub(
        lambda m: f"def {new_name}({m.group(1)}) -> None:",
        content,
        count=1,
    )


def update_docstring(
    path: Path,
    function_name: str,
    new_docstring_body: str,
    feature_slug: FeatureSlug,
    example_id: ExampleId,
) -> SyncAction | None:
    """Update the docstring and/or rename a function in a test file.

    Args:
        path: Path to the test file.
        function_name: Current function name.
        new_docstring_body: New docstring content.
        feature_slug: Current feature slug (for renaming).
        example_id: The example ID (for renaming).

    Returns:
        SyncAction if the file was changed, else None.
    """
    original = path.read_text(encoding="utf-8")
    content = original
    new_name = build_function_name(feature_slug, example_id)
    if function_name != new_name:
        content = _rename_function_in_content(content, function_name, new_name)
    content = _update_docstring_in_content(content, new_name, new_docstring_body)
    if content == original:
        return None
    path.write_text(content, encoding="utf-8")
    return SyncAction(action="UPDATE", path=path)


def _find_function_match(content: str, function_name: str) -> re.Match[str] | None:
    """Find the def line for a named function in content.

    Args:
        content: Full file content.
        function_name: The function name to find.

    Returns:
        Match object or None.
    """
    return re.search(
        rf"^def {re.escape(function_name)}\([^)]*\) -> None:",
        content,
        re.MULTILINE,
    )


def _insert_marker_before(content: str, match: re.Match[str], marker_line: str) -> str:
    """Insert a marker line before the match position in content.

    Args:
        content: Full file content.
        match: Match for the def line.
        marker_line: The marker line to insert.

    Returns:
        Updated file content.
    """
    return content[: match.start()] + marker_line + content[match.start() :]


def mark_orphan(path: Path, function_name: str) -> SyncAction | None:
    """Add an orphan skip marker before a function if not already present.

    Args:
        path: Path to the test file.
        function_name: The function to mark as orphan.

    Returns:
        SyncAction if file was changed, else None.
    """
    content = path.read_text(encoding="utf-8")
    match = _find_function_match(content, function_name)
    if not match:
        return None
    if content[: match.start()].endswith(_ORPHAN_MARKER_LINE):
        return None
    updated = _insert_marker_before(content, match, _ORPHAN_MARKER_LINE)
    path.write_text(updated, encoding="utf-8")
    return SyncAction(action="ORPHAN", path=path)


def remove_orphan_marker(path: Path, function_name: str) -> SyncAction | None:
    """Remove orphan skip marker before a function if present.

    Args:
        path: Path to the test file.
        function_name: The function to un-orphan.

    Returns:
        SyncAction if file was changed, else None.
    """
    content = path.read_text(encoding="utf-8")
    escaped_marker = re.escape(_ORPHAN_MARKER_LINE.rstrip("\n"))
    pattern = re.compile(
        rf"^{escaped_marker}\n(def {re.escape(function_name)}\([^)]*\) -> None:)",
        re.MULTILINE,
    )
    updated = pattern.sub(r"\1", content, count=1)
    if updated == content:
        return None
    path.write_text(updated, encoding="utf-8")
    return SyncAction(action="ORPHAN", path=path)


def _build_non_conforming_marker(correct_file: Path, correct_class: str | None) -> str:
    """Build the non-conforming skip marker line.

    Args:
        correct_file: Where the stub should be.
        correct_class: The correct class name, if applicable.

    Returns:
        Marker line string.
    """
    detail = f"should be in {correct_file}"
    if correct_class:
        detail += f" class {correct_class}"
    return f'@pytest.mark.skip(reason="non-conforming: {detail}")\n'


def mark_non_conforming(
    path: Path,
    function_name: str,
    correct_file: Path,
    correct_class: str | None,
) -> SyncAction | None:
    """Mark a non-conforming test function with a skip marker.

    A non-conforming stub is one in the wrong file, wrong class, or with a
    wrong function name.

    Args:
        path: Path to the test file.
        function_name: The function name to mark.
        correct_file: Where the stub should be.
        correct_class: The correct class name, if applicable.

    Returns:
        SyncAction if file was changed, else None.
    """
    marker_line = _build_non_conforming_marker(correct_file, correct_class)
    content = path.read_text(encoding="utf-8")
    match = _find_function_match(content, function_name)
    if not match:
        return None
    before_def = content[: match.start()]
    if f"non-conforming: should be in {correct_file}" in before_def:
        return None
    updated = _insert_marker_before(content, match, marker_line)
    path.write_text(updated, encoding="utf-8")
    return SyncAction(action="NON_CONFORMING", path=path)


def _rewrite_decorators(
    path: Path,
    content: str,
    match: re.Match[str],
    new_decorators: str,
) -> SyncAction:
    """Rewrite the decorator block for a match and save.

    Args:
        path: Path to the test file.
        content: Full file content.
        match: Regex match for the decorator block.
        new_decorators: Updated decorator block.

    Returns:
        SyncAction with DEPRECATED action.
    """
    indent = match.group(1)
    def_start = match.start() + len(indent) + len(match.group(2))
    new_content = content[: match.start()] + new_decorators + content[def_start:]
    path.write_text(new_content, encoding="utf-8")
    return SyncAction(action="DEPRECATED", path=path)


def _apply_deprecated_toggle(
    path: Path,
    content: str,
    match: re.Match[str],
    should_be_deprecated: bool,
) -> SyncAction | None:
    """Apply deprecated marker add/remove for a single decorator match.

    Args:
        path: Path to the test file.
        content: Full file content.
        match: Regex match for the decorator block.
        should_be_deprecated: Whether to add or remove the marker.

    Returns:
        SyncAction if changed, else None.
    """
    indent = match.group(1)
    full_decorators = indent + match.group(2)
    marker_line = f"{indent}@pytest.mark.deprecated\n"
    has_marker = marker_line in full_decorators
    if should_be_deprecated and not has_marker:
        return _rewrite_decorators(path, content, match, marker_line + full_decorators)
    if not should_be_deprecated and has_marker:
        stripped = full_decorators.replace(marker_line, "")
        return _rewrite_decorators(path, content, match, stripped)
    return None


def toggle_deprecated_marker(
    path: Path,
    function_name: str,
    *,
    should_be_deprecated: bool,
) -> SyncAction | None:
    """Add or remove @pytest.mark.deprecated before a function.

    Args:
        path: Path to the test file.
        function_name: The test function name.
        should_be_deprecated: If True, add the marker; if False, remove it.

    Returns:
        SyncAction if file was changed, else None.
    """
    if not path.exists():
        return None
    content = path.read_text(encoding="utf-8")
    for match in _DECORATOR_RE.finditer(content):
        if not function_name.endswith(f"_{match.group(3)}"):
            continue
        result = _apply_deprecated_toggle(path, content, match, should_be_deprecated)
        if result is not None:
            return result
    return None
