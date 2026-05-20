"""Gherkin feature file parser and title validation.

Parses .feature files into ScenarioInfo objects, extracting steps, placeholders,
literals, and examples tables. Also provides global title validation that checks
all feature, rule, and scenario titles for uniqueness, character set, and word
count constraints.
"""

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
    Violation,
)

_TITLE_RE = re.compile(r"^[\w\s]+$")
_PLACEHOLDER_RE = re.compile(r"<([^>]+)>")
_NUMERIC_LITERAL_RE = re.compile(r"^-?\d+$")
_QUOTED_STRING_RE = re.compile(r"""(?:"([^"]*)"|'([^']*)')""")


class GherkinError(Exception):
    """Raised when a feature file is missing, malformed, or has invalid titles."""


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
    """Extract numeric and quoted-string literals from step text.

    Quoted strings that match placeholder syntax (e.g. ``"<var>"``) are
    skipped — they represent quotes around a placeholder, not a literal
    value.

    Args:
        text: The text of a Gherkin step.

    Returns:
        A tuple of ``Literal`` objects (may be empty).

    """
    result: list[Literal] = []
    for token in text.split():
        if _NUMERIC_LITERAL_RE.match(token):
            result.append(Literal(value=int(token), raw=token))
    for match in _QUOTED_STRING_RE.finditer(text):
        value = match.group(1) if match.group(1) is not None else match.group(2)
        if _PLACEHOLDER_RE.match(value):
            continue
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
    skip_title_validation: bool = False,
) -> ScenarioInfo:
    title = sc["name"]
    if not skip_title_validation:
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
    skip_title_validation: bool = False,
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
                skip_title_validation=skip_title_validation,
            )
            scenarios.append(sc)

        if "rule" in child:
            rule = child["rule"]
            rule_title = rule["name"]
            if not skip_title_validation:
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
                        skip_title_validation=skip_title_validation,
                    )
                    scenarios.append(sc)

    return scenarios


def parse_feature(
    feature_path: Path,
    config: Config,
    seen_function_names: dict[str, str] | None = None,
    skip_title_validation: bool = False,
) -> dict[str, ScenarioInfo]:
    """Parse a single .feature file into a dict of ScenarioInfo objects.

    Extracts steps, placeholders, literals, background steps, and examples
    tables from every scenario and rule-scoped scenario.  Title validation
    runs by default but can be skipped for the inner parse pass used by
    ``check_all`` (which already calls ``validate_all_titles`` globally).

    Args:
        feature_path: Path to the ``.feature`` file.
        config: The project configuration.
        seen_function_names: Accumulator that tracks function-name collisions
            across multiple parse calls.
        skip_title_validation: When ``True``, per-title validation and duplicate
            detection inside this parse call are suppressed.

    Returns:
        A dict mapping function names to ``ScenarioInfo``.

    Raises:
        GherkinError: If the file does not exist, cannot be parsed, or contains
            no ``Feature:`` header.

    """
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
    if not skip_title_validation:
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
        skip_title_validation=skip_title_validation,
    )

    return {s.function_name: s for s in scenarios}


def _validate_single_title(
    title: str,
    kind: str,
    path: str,
    line: int,
    violations: list[Violation],
) -> bool:
    """Validate one title against the project rules.

    Rules enforced:
    1. Title must be non-empty after stripping.
    2. Title must match ``_TITLE_RE`` (Unicode letters, digits, spaces only).
    3. Title must contain 2-6 words.

    Args:
        title: The raw title string from the feature file.
        kind: One of ``"feature"``, ``"rule"``, ``"scenario"``.
        path: The feature file path (for error reporting).
        line: The source line number (for error reporting).
        violations: Mutable list that receives ``Violation`` objects for
            every rule that fails.

    Returns:
        ``True`` if the title passes all checks, ``False`` otherwise.

    """
    error_type = f"invalid-{kind}-title"

    if not title or not title.strip():
        violations.append(
            Violation(
                path=path,
                line=line,
                error_type=error_type,
                message=f"{kind.capitalize()} title must be non-empty.",
            )
        )
        return False

    if not _TITLE_RE.match(title):
        violations.append(
            Violation(
                path=path,
                line=line,
                error_type=error_type,
                message=(
                    f"{kind.capitalize()} title '{title}' contains "
                    f"invalid characters. Only Unicode letters, digits, "
                    f"and spaces are allowed."
                ),
            )
        )
        return False

    words = title.split()
    if len(words) < 2:
        violations.append(
            Violation(
                path=path,
                line=line,
                error_type=error_type,
                message=(
                    f"{kind.capitalize()} title '{title}' has "
                    f"{len(words)} word(s). Minimum 2 words required."
                ),
            )
        )
        return False
    if len(words) > 6:
        violations.append(
            Violation(
                path=path,
                line=line,
                error_type=error_type,
                message=(
                    f"{kind.capitalize()} title '{title}' has "
                    f"{len(words)} words. Maximum 6 words allowed."
                ),
            )
        )
        return False

    return True


def _register_title(
    title: str,
    kind: str,
    path: str,
    line: int,
    seen: dict[str, list[tuple[str, str, str, int]]],
) -> None:
    """Record a validated title in the case-insensitive duplicate tracker.

    Titles are normalised to lower case for comparison so ``"Hive Activity"``
    and ``"hive activity"`` map to the same key.

    Args:
        title: The validated title string.
        kind: One of ``"feature"``, ``"rule"``, ``"scenario"``.
        path: The feature file path.
        line: The source line number.
        seen: Mutable dict that accumulates title entries keyed by lower-cased
            title.

    """
    key = title.strip().lower()
    seen.setdefault(key, []).append((title.strip(), kind, path, line))


def _emit_duplicates(
    seen: dict[str, list[tuple[str, str, str, int]]],
    violations: list[Violation],
) -> None:
    """Emit duplicate-title violations from the accumulated registry.

    When the same title key is used by more than one entity, a violation is
    reported for the *lowest-priority* kind (scenario preferred over rule,
    rule over feature) so that one logical "owner" is considered the
    original and the others are flagged as duplicates.

    Args:
        seen: Accumulator dict from ``_register_title``.
        violations: Mutable list that receives ``Violation`` objects.

    """
    kind_priority = {"scenario": 0, "rule": 1, "feature": 2}

    for entries in seen.values():
        if len(entries) > 1:
            kinds = {kind for _, kind, _, _ in entries}
            report_kind = min(kinds, key=lambda k: kind_priority[k])

            for title, kind, path, line in entries:
                if kind != report_kind:
                    continue
                violations.append(
                    Violation(
                        path=path,
                        line=line,
                        error_type=f"duplicate-{kind}-title",
                        message=(
                            f"Duplicate {kind} title '{title}' "
                            f"(case-insensitive match with "
                            f"'{entries[0][0]}')."
                        ),
                    )
                )


def detect_empty_rules(doc: dict) -> bool:
    """Return True if the feature document has any rules with no scenarios.

    A rule is "empty" when it has no scenario children. Features with no
    rules at all return ``False`` — only rules that exist but lack scenarios
    are considered empty.

    Args:
        doc: The parsed feature document dict from ``Parser().parse()``.

    Returns:
        ``True`` if at least one rule exists with zero scenario children.

    """
    feature = doc.get("feature")
    if not feature:
        return False
    for child in feature.get("children", []):
        if "rule" in child:
            rule = child["rule"]
            rule_children = rule.get("children", [])
            if not any("scenario" in rc for rc in rule_children):
                return True
    return False


def validate_all_titles(config: Config) -> list[Violation]:
    """Validate all titles across every ``.feature`` file in the project.

    Scans the features directory, extracts every Feature, Rule, and Scenario
    title, and checks:
    - Character-set validity (``_TITLE_RE``).
    - Non-empty requirement.
    - Word-count bounds (2-6 words).
    - Case-insensitive uniqueness across the whole project.

    Used as a pre-flight gate in ``generate_stubs`` and as the final step in
    ``check_all``.

    Args:
        config: The project configuration.

    Returns:
        A (possibly empty) list of ``Violation`` objects.  Each violation
        carries an ``error_type`` of ``invalid-{kind}-title`` or
        ``duplicate-{kind}-title``.

    """
    features_dir = Path(config.features_dir)
    if not features_dir.is_dir():
        return []

    violations: list[Violation] = []
    seen: dict[str, list[tuple[str, str, str, int]]] = {}

    for feature_path in sorted(features_dir.rglob("*.feature")):
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
        feature_line = feature.get("location", {}).get("line", 1)
        if _validate_single_title(
            feature_title, "feature", str(feature_path), feature_line, violations
        ):
            _register_title(
                feature_title, "feature", str(feature_path), feature_line, seen
            )

        for child in feature.get("children", []):
            if "rule" in child:
                rule = child["rule"]
                rule_title = rule["name"]
                rule_line = rule.get("location", {}).get("line", 1)
                if _validate_single_title(
                    rule_title, "rule", str(feature_path), rule_line, violations
                ):
                    _register_title(
                        rule_title, "rule", str(feature_path), rule_line, seen
                    )
                for rc in rule.get("children", []):
                    if "scenario" in rc:
                        sc = rc["scenario"]
                        sc_title = sc["name"]
                        sc_line = sc.get("location", {}).get("line", 1)
                        if _validate_single_title(
                            sc_title,
                            "scenario",
                            str(feature_path),
                            sc_line,
                            violations,
                        ):
                            _register_title(
                                sc_title,
                                "scenario",
                                str(feature_path),
                                sc_line,
                                seen,
                            )
            elif "scenario" in child:
                sc = child["scenario"]
                sc_title = sc["name"]
                sc_line = sc.get("location", {}).get("line", 1)
                if _validate_single_title(
                    sc_title, "scenario", str(feature_path), sc_line, violations
                ):
                    _register_title(
                        sc_title, "scenario", str(feature_path), sc_line, seen
                    )

    _emit_duplicates(seen, violations)
    return violations
