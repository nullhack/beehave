"""Gherkin parse model — typed tree returned by `parse_feature`."""

from __future__ import annotations

import re
from typing import Any, cast

from gherkin.parser import Parser


class Placeholder:
    """A captured `<name>` placeholder found inside a step's text."""

    name: str


class DataTable:
    """Optional table on a step; `headers` is None when header-less."""

    headers: list[str] | None
    rows: list[list[str]]


class Step:
    """One Gherkin step: keyword, text, placeholders, optional docstring/table."""

    keyword: str
    text: str
    placeholders: list[Placeholder]
    docstring: str | None
    data_table: DataTable | None


class Examples:
    """The `Examples:` block of a Scenario Outline."""

    headers: list[str]
    rows: list[dict[str, str]]


class Background:
    """Shared steps prepended to every scenario in the enclosing feature or rule."""

    steps: list[Step]


class Scenario:
    """A scenario with merged background + own steps and optional examples."""

    title: str
    slug: str
    function_name: str
    tags: list[str]
    keyword: str
    steps: list[Step]
    examples: Examples | None


class Rule:
    """A `Rule:` block — name, tags, optional background, and child scenarios."""

    name: str
    tags: list[str]
    background: Background | None
    children: list[Scenario]


class Feature:
    """The parsed feature — top-level scenarios and rules."""

    name: str
    tags: list[str]
    background: Background | None
    children: list[Rule | Scenario]


_PLACEHOLDER_RE = re.compile(r"<([^>]+)>")
_WHITESPACE_RE = re.compile(r"\s+")

_MIN_WORD_COUNT = 2
_MAX_WORD_COUNT = 6


def _make_placeholder(name: str) -> Placeholder:
    p = Placeholder()
    p.name = name
    return p


def _make_data_table(headers: list[str] | None, rows: list[list[str]]) -> DataTable:
    dt = DataTable()
    dt.headers = headers
    dt.rows = rows
    return dt


def _make_step(
    *,
    keyword: str,
    text: str,
    placeholders: list[Placeholder],
    docstring: str | None,
    data_table: DataTable | None,
) -> Step:
    s = Step()
    s.keyword = keyword
    s.text = text
    s.placeholders = placeholders
    s.docstring = docstring
    s.data_table = data_table
    return s


def _make_examples(headers: list[str], rows: list[dict[str, str]]) -> Examples:
    e = Examples()
    e.headers = headers
    e.rows = rows
    return e


def _make_background(steps: list[Step]) -> Background:
    b = Background()
    b.steps = steps
    return b


def _make_scenario(
    *,
    title: str,
    slug: str,
    function_name: str,
    tags: list[str],
    keyword: str,
    steps: list[Step],
    examples: Examples | None,
) -> Scenario:
    s = Scenario()
    s.title = title
    s.slug = slug
    s.function_name = function_name
    s.tags = tags
    s.keyword = keyword
    s.steps = steps
    s.examples = examples
    return s


def _make_rule(
    *,
    name: str,
    tags: list[str],
    background: Background | None,
    children: list[Scenario],
) -> Rule:
    r = Rule()
    r.name = name
    r.tags = tags
    r.background = background
    r.children = children
    return r


def _make_feature(
    *,
    name: str,
    tags: list[str],
    background: Background | None,
    children: list[Rule | Scenario],
) -> Feature:
    f = Feature()
    f.name = name
    f.tags = tags
    f.background = background
    f.children = children
    return f


def _placeholders_from(text: str) -> list[Placeholder]:
    seen: set[str] = set()
    result: list[Placeholder] = []
    for match in _PLACEHOLDER_RE.finditer(text):
        name = match.group(1)
        if name in seen:
            continue
        seen.add(name)
        result.append(_make_placeholder(name))
    return result


def _data_table_from(data: dict[str, Any]) -> DataTable:
    rows_raw = data.get("rows") or []
    cells = [[c["value"] for c in row.get("cells", [])] for row in rows_raw]
    if not cells:
        return _make_data_table(headers=None, rows=[])
    return _make_data_table(headers=cells[0], rows=cells[1:])


def _step_from(data: dict[str, Any]) -> Step:
    text = data["text"]
    dt = data.get("dataTable")
    doc_string = data.get("docString")
    return _make_step(
        keyword=data["keyword"].strip(),
        text=text,
        placeholders=_placeholders_from(text),
        docstring=doc_string.get("content") if doc_string else None,
        data_table=_data_table_from(dt) if dt else None,
    )


def _background_from(data: dict[str, Any]) -> Background:
    return _make_background(steps=[_step_from(s) for s in data.get("steps", [])])


def _examples_from(ex_list: list[dict[str, Any]]) -> Examples | None:
    if not ex_list:
        return None
    ex = ex_list[0]
    header_row = ex.get("tableHeader") or {}
    headers = [c["value"] for c in header_row.get("cells", [])]
    rows: list[dict[str, str]] = []
    for row in ex.get("tableBody", []):
        cells = [c["value"] for c in row.get("cells", [])]
        rows.append(dict(zip(headers, cells, strict=False)))
    return _make_examples(headers=headers, rows=rows)


def _slug_from(title: str) -> str:
    return _WHITESPACE_RE.sub("_", title.strip()).lower()


def _validate_single_title(title: str, kind: str) -> None:
    if not title or not title.strip():
        raise ValueError(f"{kind} title must be non-empty")
    for ch in title:
        if not (ch.isspace() or ch.isalpha() or ch.isdigit()):
            raise ValueError(
                f"{kind} title {title!r} contains invalid character {ch!r}; "
                f"only Unicode letters, digits, and spaces are allowed"
            )
    words = title.split()
    if len(words) < _MIN_WORD_COUNT or len(words) > _MAX_WORD_COUNT:
        raise ValueError(
            f"{kind} title {title!r} has {len(words)} word(s); "
            f"must be {_MIN_WORD_COUNT}-{_MAX_WORD_COUNT}"
        )


def _reject_duplicate(title: str, kind: str, seen: set[str]) -> None:
    key = title.strip().lower()
    if key in seen:
        raise ValueError(f"Duplicate {kind} title {title!r} (case-insensitive match)")
    seen.add(key)


def _reject_background_placeholders(background: Background) -> None:
    for step in background.steps:
        if step.placeholders:
            raise ValueError(
                f"Background step {step.text!r} contains placeholder "
                f"<{step.placeholders[0].name}>; "
                f"background steps must be placeholder-free"
            )


def _first_background_from(children: list[dict[str, Any]]) -> Background | None:
    for child in children:
        if "background" in child:
            bg = _background_from(child["background"])
            _reject_background_placeholders(bg)
            return bg
    return None


def _scenario_from(
    data: dict[str, Any],
    merged_steps: list[Step],
    seen: set[str],
) -> Scenario:
    title = data["name"]
    _validate_single_title(title, "scenario")
    _reject_duplicate(title, "scenario", seen)
    slug = _slug_from(title)
    own_steps = [_step_from(s) for s in data.get("steps", [])]
    return _make_scenario(
        title=title,
        slug=slug,
        function_name=f"test_{slug}",
        tags=[t["name"] for t in data.get("tags", [])],
        keyword=data["keyword"],
        steps=[*merged_steps, *own_steps],
        examples=_examples_from(data.get("examples", [])),
    )


def _rule_from(
    data: dict[str, Any],
    feature_bg_steps: list[Step],
    seen: set[str],
) -> Rule:
    name = data["name"]
    _reject_duplicate(name, "rule", seen)
    rule_bg = _first_background_from(data.get("children", []))
    rule_bg_steps = rule_bg.steps if rule_bg else []
    children: list[Scenario] = []
    for rc in data.get("children", []):
        if "scenario" in rc:
            children.append(
                _scenario_from(
                    rc["scenario"],
                    [*feature_bg_steps, *rule_bg_steps],
                    seen,
                )
            )
    return _make_rule(
        name=name,
        tags=[t["name"] for t in data.get("tags", [])],
        background=rule_bg,
        children=children,
    )


def parse_feature(source: str) -> Feature:
    """Parse `.feature` source into a `Feature`, enforcing title rules.

    Scenario titles must use Unicode letters/digits/spaces only, span two
    to six words, and be case-insensitively unique within the feature.
    Placeholders in any background step are rejected at parse time.
    """
    doc = cast(dict[str, Any], Parser().parse(source))
    feature_data = cast(dict[str, Any], doc.get("feature") or {})

    background = _first_background_from(feature_data.get("children", []))
    feature_bg_steps = background.steps if background else []

    # Title rules enforce at parse time on every scenario title (charset +
    # 2-6 word count + case-insensitive uniqueness). Feature and Rule names
    # join the case-insensitive uniqueness set (data-model §2.1/§2.2 carry
    # only a non-empty constraint, so charset/word-count do not apply to
    # them — `Feature: Parsing` and `Feature: T` in the test fixtures are
    # both one word). Background placeholder rejection is independent.
    seen: set[str] = set()
    feature_name = feature_data.get("name", "")
    if feature_name:
        seen.add(feature_name.strip().lower())

    children: list[Rule | Scenario] = []
    for child in feature_data.get("children", []):
        if "scenario" in child:
            children.append(_scenario_from(child["scenario"], feature_bg_steps, seen))
        elif "rule" in child:
            children.append(_rule_from(child["rule"], feature_bg_steps, seen))

    return _make_feature(
        name=feature_name,
        tags=[t["name"] for t in feature_data.get("tags", [])],
        background=background,
        children=children,
    )
