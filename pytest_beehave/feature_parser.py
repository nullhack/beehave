"""Gherkin feature file parser for pytest-beehave."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, cast

from gherkin import Parser as _GherkinParserImpl

from pytest_beehave.models import ExampleId, FeatureSlug, RuleSlug

_ID_TAG_RE: re.Pattern[str] = re.compile(r"@id:(\S+)")


class GherkinParserProtocol(Protocol):
    """Protocol for a Gherkin file parser."""

    def parse(self, text: str) -> dict[str, Any]:  # pragma: no cover
        """Parse Gherkin text into an AST dict."""
        ...


class GherkinParser:
    """Adapter wrapping the gherkin library Parser to match GherkinParserProtocol."""

    def __init__(self) -> None:
        """Initialise the underlying gherkin parser."""
        self._impl = _GherkinParserImpl()

    def parse(self, text: str) -> dict[str, Any]:
        """Parse Gherkin text into an AST dict.

        Args:
            text: The Gherkin feature file content.

        Returns:
            AST as a dict.
        """
        return cast(dict[str, Any], self._impl.parse(text))


@dataclass(frozen=True, slots=True)
class ParsedStep:
    """A single step line parsed from a Gherkin Example.

    Attributes:
        keyword: The step keyword (Given, When, Then, And, But, *).
        text: The step text.
        doc_string: Optional attached doc string content.
        data_table: Optional rendered data table string.
    """

    keyword: str
    text: str
    doc_string: str | None
    data_table: str | None


@dataclass(frozen=True, slots=True)
class ParsedExample:
    """A single Example parsed from a .feature file.

    Attributes:
        example_id: The @id hex identifier.
        steps: Tuple of parsed steps.
        background_sections: Background step tuples (feature-level then rule-level).
        outline_examples: Rendered Examples table string, if Scenario Outline.
        is_deprecated: True if tagged @deprecated.
    """

    example_id: ExampleId
    steps: tuple[ParsedStep, ...]
    background_sections: tuple[tuple[ParsedStep, ...], ...]
    outline_examples: str | None
    is_deprecated: bool


@dataclass(frozen=True, slots=True)
class ParsedRule:
    """A Rule block parsed from a feature file.

    Attributes:
        title: The Rule: title text.
        rule_slug: Slugified rule title (underscore-separated).
        examples: Tuple of parsed examples in this rule.
        is_deprecated: True if the rule itself is deprecated.
    """

    title: str
    rule_slug: RuleSlug
    examples: tuple[ParsedExample, ...]
    is_deprecated: bool


@dataclass(frozen=True, slots=True)
class ParsedFeature:
    """A fully parsed .feature file.

    Attributes:
        path: Path to the .feature file.
        feature_slug: Slugified feature folder name (underscore-separated).
        rules: Tuple of parsed rules (may be empty if no Rule blocks).
        top_level_examples: Examples not inside any Rule block.
        is_deprecated: True if the feature is deprecated.
    """

    path: Path
    feature_slug: FeatureSlug
    rules: tuple[ParsedRule, ...]
    top_level_examples: tuple[ParsedExample, ...]
    is_deprecated: bool

    def all_example_ids(self) -> set[ExampleId]:
        """Collect all example IDs from rules and top-level examples.

        Returns:
            Set of ExampleId objects.
        """
        ids: set[ExampleId] = {ex.example_id for ex in self.top_level_examples}
        for rule in self.rules:
            ids.update(ex.example_id for ex in rule.examples)
        return ids


def _compute_col_widths(all_cells: list[list[str]]) -> list[int]:
    """Compute maximum column widths across all rows.

    Args:
        all_cells: List of rows, each row is a list of cell value strings.

    Returns:
        List of column widths.
    """
    col_count = max(len(row) for row in all_cells)
    return [
        max(len(row[col]) for row in all_cells if col < len(row))
        for col in range(col_count)
    ]


def _render_padded_row(row_cells: list[str], col_widths: list[int]) -> str:
    """Render a table row with padded cells.

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
    """Render a Gherkin data table as a multi-line string.

    Args:
        rows: List of row dicts with 'cells' lists.

    Returns:
        Rendered table string.
    """
    if not rows:
        return ""
    all_cells = [
        [cell.get("value", "") for cell in row.get("cells", [])] for row in rows
    ]
    col_widths = _compute_col_widths(all_cells)
    return "\n".join(_render_padded_row(row, col_widths) for row in all_cells)


def _render_examples_table(examples: list[dict[str, Any]]) -> str:
    """Render the Examples table from a Scenario Outline.

    Args:
        examples: List of examples dicts from the Gherkin AST.

    Returns:
        Rendered Examples table, or empty string if none.
    """
    if not examples:
        return ""
    header = examples[0].get("tableHeader")
    body = examples[0].get("tableBody", [])
    all_rows: list[list[str]] = []
    if header:
        all_rows.append([cell.get("value", "") for cell in header.get("cells", [])])
    for row in body:
        all_rows.append([cell.get("value", "") for cell in row.get("cells", [])])
    if not all_rows:
        return "Examples:"
    col_widths = _compute_col_widths(all_rows)
    lines = ["Examples:"] + [
        "  " + _render_padded_row(row, col_widths) for row in all_rows
    ]
    return "\n".join(lines)


def _build_step(raw: dict[str, Any]) -> ParsedStep:
    """Build a ParsedStep from a Gherkin AST step dict.

    Args:
        raw: A step dict from the Gherkin AST.

    Returns:
        A ParsedStep.
    """
    doc_string: str | None = None
    data_table: str | None = None
    if "docString" in raw:
        doc_string = raw["docString"].get("content", "")
    if "dataTable" in raw:
        data_table = _render_data_table(raw["dataTable"].get("rows", []))
    return ParsedStep(
        keyword=raw["keyword"].strip(),
        text=raw.get("text", ""),
        doc_string=doc_string,
        data_table=data_table,
    )


def _build_steps(raw_steps: list[dict[str, Any]]) -> tuple[ParsedStep, ...]:
    """Build a tuple of ParsedStep from AST step list.

    Args:
        raw_steps: List of step dicts.

    Returns:
        Tuple of ParsedStep.
    """
    return tuple(_build_step(s) for s in raw_steps)


def _extract_background(
    children: list[dict[str, Any]],
) -> tuple[ParsedStep, ...] | None:
    """Extract background steps from a list of AST children.

    Args:
        children: Child dicts from the Gherkin AST.

    Returns:
        Tuple of ParsedStep, or None if no Background.
    """
    for child in children:
        background = child.get("background")
        if background is not None:
            return _build_steps(background.get("steps", []))
    return None


def _extract_id_from_tags(tags: list[dict[str, Any]]) -> str | None:
    """Find the @id:<hex> value from Gherkin AST tags.

    Args:
        tags: List of tag dicts.

    Returns:
        8-char hex ID or None.
    """
    for tag in tags:
        match = _ID_TAG_RE.search(tag.get("name", ""))
        if match:
            return match.group(1)
    return None


def _has_deprecated_tag(tags: list[dict[str, Any]]) -> bool:
    """Check if @deprecated tag is present.

    Args:
        tags: List of tag dicts.

    Returns:
        True if @deprecated is found.
    """
    return any(t["name"] == "@deprecated" for t in tags)


def _collect_background_sections(
    feature_bg: tuple[ParsedStep, ...] | None,
    rule_bg: tuple[ParsedStep, ...] | None,
) -> tuple[tuple[ParsedStep, ...], ...]:
    """Collect non-None background step tuples in order.

    Args:
        feature_bg: Feature-level background steps.
        rule_bg: Rule-level background steps.

    Returns:
        Tuple of background step tuples.
    """
    sections = [bg for bg in (feature_bg, rule_bg) if bg is not None]
    return tuple(sections)


def _build_example(
    scenario: dict[str, Any],
    feature_bg: tuple[ParsedStep, ...] | None,
    rule_bg: tuple[ParsedStep, ...] | None,
    parent_deprecated: bool = False,
) -> ParsedExample | None:
    """Build a ParsedExample from a scenario dict.

    Args:
        scenario: Gherkin AST scenario dict.
        feature_bg: Feature-level background steps.
        rule_bg: Rule-level background steps.
        parent_deprecated: True if a parent (rule or feature) is deprecated.

    Returns:
        ParsedExample or None if no @id tag.
    """
    tags = scenario.get("tags", [])
    id_str = _extract_id_from_tags(tags)
    if id_str is None:
        return None
    outline_examples = scenario.get("examples", [])
    return ParsedExample(
        example_id=ExampleId(id_str),
        steps=_build_steps(scenario.get("steps", [])),
        background_sections=_collect_background_sections(feature_bg, rule_bg),
        outline_examples=(
            _render_examples_table(outline_examples) if outline_examples else None
        ),
        is_deprecated=parent_deprecated or _has_deprecated_tag(tags),
    )


def _example_from_child(
    child: dict[str, Any],
    feature_bg: tuple[ParsedStep, ...] | None,
    rule_bg: tuple[ParsedStep, ...] | None,
    rule_deprecated: bool,
) -> ParsedExample | None:
    """Return a ParsedExample from a rule child dict, or None if not a scenario.

    Args:
        child: A child dict from the rule's Gherkin AST.
        feature_bg: Feature-level background steps.
        rule_bg: Rule-level background steps.
        rule_deprecated: True if the rule is deprecated.

    Returns:
        ParsedExample or None.
    """
    scenario = child.get("scenario")
    if scenario is None:
        return None
    return _build_example(scenario, feature_bg, rule_bg, rule_deprecated)


def _parse_rule_examples(
    rule_children: list[dict[str, Any]],
    feature_bg: tuple[ParsedStep, ...] | None,
    rule_bg: tuple[ParsedStep, ...] | None,
    rule_deprecated: bool,
) -> tuple[ParsedExample, ...]:
    """Parse all examples from rule children.

    Args:
        rule_children: Child dicts from the rule's Gherkin AST.
        feature_bg: Feature-level background steps.
        rule_bg: Rule-level background steps.
        rule_deprecated: True if the rule is deprecated.

    Returns:
        Tuple of ParsedExample.
    """
    candidates = (
        _example_from_child(child, feature_bg, rule_bg, rule_deprecated)
        for child in rule_children
    )
    return tuple(ex for ex in candidates if ex is not None)


def _parse_rule(
    rule: dict[str, Any],
    feature_bg: tuple[ParsedStep, ...] | None,
    feature_deprecated: bool = False,
) -> ParsedRule:
    """Parse a Rule block into a ParsedRule.

    Args:
        rule: Rule dict from the Gherkin AST.
        feature_bg: Feature-level background steps.
        feature_deprecated: True if the parent feature is deprecated.

    Returns:
        A ParsedRule.
    """
    title = rule.get("name", "")
    rule_children = rule.get("children", [])
    rule_deprecated = feature_deprecated or _has_deprecated_tag(rule.get("tags", []))
    rule_bg = _extract_background(rule_children)
    examples = _parse_rule_examples(rule_children, feature_bg, rule_bg, rule_deprecated)
    return ParsedRule(
        title=title,
        rule_slug=RuleSlug.from_rule_title(title),
        examples=examples,
        is_deprecated=rule_deprecated,
    )


def _empty_feature(path: Path, feature_slug: FeatureSlug) -> ParsedFeature:
    """Return an empty ParsedFeature for a file with no feature block.

    Args:
        path: Path to the .feature file.
        feature_slug: The feature slug.

    Returns:
        ParsedFeature with no rules or examples.
    """
    return ParsedFeature(
        path=path,
        feature_slug=feature_slug,
        rules=(),
        top_level_examples=(),
        is_deprecated=False,
    )


def _parse_child(
    child: dict[str, Any],
    feature_bg: tuple[ParsedStep, ...] | None,
    feature_deprecated: bool,
    rules: list[ParsedRule],
    top_level: list[ParsedExample],
) -> None:
    """Parse one feature child into rules or top-level examples.

    Args:
        child: A child dict from the Gherkin AST.
        feature_bg: Feature-level background steps.
        feature_deprecated: True if the feature is deprecated.
        rules: List to append ParsedRule to.
        top_level: List to append ParsedExample to.
    """
    rule_node = child.get("rule")
    if rule_node is not None:
        rules.append(_parse_rule(rule_node, feature_bg, feature_deprecated))
        return
    scenario = child.get("scenario")
    if scenario is None:
        return
    ex = _build_example(scenario, feature_bg, None, feature_deprecated)
    if ex is not None:
        top_level.append(ex)


def _parse_children(
    children: list[dict[str, Any]],
    feature_bg: tuple[ParsedStep, ...] | None,
    feature_deprecated: bool,
) -> tuple[tuple[ParsedRule, ...], tuple[ParsedExample, ...]]:
    """Parse the children of a feature block into rules and top-level examples.

    Args:
        children: Child dicts from the Gherkin AST.
        feature_bg: Feature-level background steps.
        feature_deprecated: True if the feature is deprecated.

    Returns:
        Tuple of (rules, top_level_examples).
    """
    rules: list[ParsedRule] = []
    top_level: list[ParsedExample] = []
    for child in children:
        _parse_child(child, feature_bg, feature_deprecated, rules, top_level)
    return tuple(rules), tuple(top_level)


def parse_feature(
    path: Path,
    folder_name: str | None = None,
    parser: GherkinParserProtocol | None = None,
) -> ParsedFeature:
    """Parse a .feature file into a ParsedFeature.

    Args:
        path: Path to the .feature file.
        folder_name: The feature folder name. Defaults to path.parent.name.
        parser: Optional Gherkin parser instance. Defaults to GherkinParser().

    Returns:
        A ParsedFeature with all examples.
    """
    if folder_name is None:
        parent = path.parent
        folder_name = parent.name
    if parser is None:
        parser = GherkinParser()
    doc = parser.parse(path.read_text(encoding="utf-8"))
    feature = cast(dict[str, Any] | None, doc.get("feature"))
    feature_slug = FeatureSlug.from_folder_name(folder_name)
    if not feature:
        return _empty_feature(path, feature_slug)
    children = feature.get("children", [])
    feature_deprecated = _has_deprecated_tag(feature.get("tags", []))
    feature_bg = _extract_background(children)
    rules, top_level = _parse_children(children, feature_bg, feature_deprecated)
    return ParsedFeature(
        path=path,
        feature_slug=feature_slug,
        rules=rules,
        top_level_examples=top_level,
        is_deprecated=feature_deprecated,
    )


def collect_all_example_ids(feature: ParsedFeature) -> set[ExampleId]:
    """Collect all example IDs from a parsed feature.

    Args:
        feature: A ParsedFeature.

    Returns:
        Set of ExampleId objects.
    """
    return feature.all_example_ids()
