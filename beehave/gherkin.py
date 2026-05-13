from __future__ import annotations

import builtins
import keyword
import re
from pathlib import Path

from gherkin import Parser

from beehave.config import Config
from beehave.models import (
    ExamplesTable,
    Literal,
    ParsedStep,
    Placeholder,
    ScenarioInfo,
)

_TITLE_RE = re.compile(r"^[\w\s]+$")
_PLACEHOLDER_RE = re.compile(r"<([^>]+)>")
_NUMERIC_LITERAL_RE = re.compile(r"^-?\d+$")
_QUOTED_STRING_RE = re.compile(r"""(?:"([^"]*)"|'([^']*)')""")


class GherkinError(Exception):
    pass


def _validate_title(title: str, kind: str, context: str = "") -> None:
    if not title or not title.strip():
        raise GherkinError(f"{kind} title must be non-empty. {context}")
    if not _TITLE_RE.match(title):
        raise GherkinError(
            f"{kind} title '{title}' contains invalid characters. "
            f"Only Unicode letters, digits, and spaces are allowed. "
            f"{context}"
        )


def _derive_path_slug(title: str) -> str:
    return re.sub(r"\s+", "_", title.strip()).lower()


def _derive_function_name(title: str) -> str:
    trimmed = title.strip()
    collapsed = re.sub(r"\s+", "_", trimmed).lower()
    name = f"test_{collapsed}"
    if not name.isidentifier():
        raise GherkinError(
            f"Derived function name '{name}' is not a valid Python "
            f"identifier from scenario title '{title}'"
        )
    return name


_derive_feature_path = _derive_rule_path = _derive_path_slug


def _extract_placeholders(text: str) -> tuple[Placeholder, ...]:
    seen: set[str] = set()
    result: list[Placeholder] = []
    for match in _PLACEHOLDER_RE.finditer(text):
        name = match.group(1)
        if name in seen:
            continue
        if not name.isidentifier():
            raise GherkinError(
                f"Placeholder '<{name}>' is not a valid Python identifier"
            )
        if keyword.iskeyword(name):
            raise GherkinError(f"Placeholder '<{name}>' is a Python keyword")
        if hasattr(builtins, name):
            raise GherkinError(f"Placeholder '<{name}>' shadows a Python builtin")
        seen.add(name)
        result.append(Placeholder(name=name))
    return tuple(result)


def _extract_literals(text: str) -> tuple[Literal, ...]:
    result: list[Literal] = []
    for token in text.split():
        if _NUMERIC_LITERAL_RE.match(token):
            result.append(Literal(value=int(token), raw=token))
    for match in _QUOTED_STRING_RE.finditer(text):
        value = match.group(1) if match.group(1) is not None else match.group(2)
        result.append(Literal(value=value, raw=match.group(0)))
    return tuple(result)


def _parse_step(step_data: dict) -> ParsedStep:
    text = step_data["text"]
    return ParsedStep(
        keyword=step_data["keyword"].strip(),
        text=text,
        placeholders=_extract_placeholders(text),
        literals=_extract_literals(text),
        line=step_data["location"]["line"],
    )


def _parse_examples(
    examples_list: list[dict],
) -> ExamplesTable | None:
    if not examples_list:
        return None
    ex = examples_list[0]
    headers = tuple(h["value"] for h in ex.get("tableHeader", {}).get("cells", []))
    rows: list[tuple[str, ...]] = []
    for row in ex.get("tableBody", []):
        rows.append(tuple(cell["value"] for cell in row["cells"]))
    if not rows:
        return None
    return ExamplesTable(headers=headers, rows=tuple(rows))


def _check_no_placeholders(steps: list[ParsedStep]) -> None:
    for step in steps:
        if step.placeholders:
            raise GherkinError(
                f"Background step '{step.text}' contains placeholder "
                f"'<{step.placeholders[0].name}>'. "
                f"Background steps must contain no placeholders."
            )


def _collect_placeholders(
    steps: list[ParsedStep],
) -> tuple[Placeholder, ...]:
    all_ph: list[Placeholder] = []
    seen: set[str] = set()
    for step in steps:
        for ph in step.placeholders:
            if ph.name not in seen:
                seen.add(ph.name)
                all_ph.append(ph)
    return tuple(all_ph)


def _collect_literals(
    scenario_steps: list[ParsedStep],
    bg_steps: list[ParsedStep],
    check_numeric: bool,
    check_string: bool,
) -> tuple[Literal, ...]:
    literals: list[Literal] = []
    for step in scenario_steps:
        literals.extend(step.literals)
    for step in bg_steps:
        for lit in step.literals:
            if (isinstance(lit.value, str) and check_string) or (
                isinstance(lit.value, int) and check_numeric
            ):
                literals.append(lit)
    return tuple(literals)


def _build_scenario(
    sc: dict,
    feature_title: str,
    feature_path: str,
    rule_path: str,
    feature_bg: list[ParsedStep],
    rule_bg: list[ParsedStep],
    check_numeric: bool,
    check_string: bool,
    seen_fn: dict[str, str],
) -> ScenarioInfo:
    title = sc["name"]
    _validate_title(title, "Scenario", f"Feature: {feature_title}")

    function_name = _derive_function_name(title)
    if function_name in seen_fn:
        raise GherkinError(
            f"Scenario title '{title}' produces function name "
            f"'{function_name}' which collides with scenario in "
            f"feature '{seen_fn[function_name]}'"
        )
    seen_fn[function_name] = feature_title

    steps = [_parse_step(s) for s in sc.get("steps", [])]
    merged = feature_bg + rule_bg + steps

    examples = _parse_examples(sc.get("examples", []))
    is_outline = bool(examples)

    if is_outline and not examples.rows:
        raise GherkinError(
            f"Scenario Outline '{title}' must have at least one "
            f"Examples table with at least one data row"
        )

    return ScenarioInfo(
        title=title,
        function_name=function_name,
        steps=tuple(merged),
        placeholders=_collect_placeholders(merged),
        literals=_collect_literals(
            steps, feature_bg + rule_bg, check_numeric, check_string
        ),
        examples=examples,
        is_outline=is_outline,
        feature_title=feature_title,
        feature_path=feature_path,
        rule_path=rule_path,
        line=sc["location"]["line"],
    )


def _collect_scenarios_from_children(
    children: list[dict],
    feature_title: str,
    feature_path: str,
    feature_bg: list[ParsedStep],
    check_numeric: bool,
    check_string: bool,
    seen_fn: dict[str, str],
) -> list[ScenarioInfo]:
    scenarios: list[ScenarioInfo] = []
    for child in children:
        if "background" in child:
            continue

        if "scenario" in child:
            sc = _build_scenario(
                sc=child["scenario"],
                feature_title=feature_title,
                feature_path=feature_path,
                rule_path="default_test",
                feature_bg=feature_bg,
                rule_bg=[],
                check_numeric=check_numeric,
                check_string=check_string,
                seen_fn=seen_fn,
            )
            scenarios.append(sc)

        if "rule" in child:
            rule = child["rule"]
            rule_title = rule["name"]
            _validate_title(rule_title, "Rule", f"Feature: {feature_title}")
            rp = _derive_rule_path(rule_title) + "_test"

            rule_bg: list[ParsedStep] = []
            for rc in rule.get("children", []):
                if "background" in rc:
                    bg_steps = [
                        _parse_step(s) for s in rc["background"].get("steps", [])
                    ]
                    _check_no_placeholders(bg_steps)
                    rule_bg = bg_steps
                    break

            for rc in rule.get("children", []):
                if "scenario" in rc:
                    sc = _build_scenario(
                        sc=rc["scenario"],
                        feature_title=feature_title,
                        feature_path=feature_path,
                        rule_path=rp,
                        feature_bg=feature_bg,
                        rule_bg=rule_bg,
                        check_numeric=check_numeric,
                        check_string=check_string,
                        seen_fn=seen_fn,
                    )
                    scenarios.append(sc)

    return scenarios


def parse_feature(
    feature_path: Path,
    config: Config,
    seen_function_names: dict[str, str] | None = None,
) -> dict[str, ScenarioInfo]:
    if not feature_path.exists():
        raise GherkinError(f"Feature file not found: {feature_path}")

    try:
        content = feature_path.read_text(encoding="utf-8")
        doc = Parser().parse(content)
    except Exception as e:
        line = getattr(e, "line", 0) or 0
        raise GherkinError(f"{feature_path}:{line}: {e}") from e

    feature = doc.get("feature")
    if not feature:
        raise GherkinError(f"No feature found in {feature_path}")

    feature_title = feature["name"]
    _validate_title(feature_title, "Feature")
    feature_path_str = _derive_feature_path(feature_title)

    if seen_function_names is None:
        seen_function_names = {}

    feature_bg: list[ParsedStep] = []
    children = feature.get("children", [])

    for child in children:
        if "background" in child:
            bg_steps = [_parse_step(s) for s in child["background"].get("steps", [])]
            _check_no_placeholders(bg_steps)
            feature_bg = bg_steps
            break

    scenarios = _collect_scenarios_from_children(
        children=children,
        feature_title=feature_title,
        feature_path=feature_path_str,
        feature_bg=feature_bg,
        check_numeric=config.background_check_numeric,
        check_string=config.background_check_string,
        seen_fn=seen_function_names,
    )

    return {s.function_name: s for s in scenarios}
