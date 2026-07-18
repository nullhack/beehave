from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from beehave.gherkin import Rule, parse_feature

if TYPE_CHECKING:
    from beehave.gherkin import Examples, Scenario, Step


def _slug_from(title: str) -> str:
    return "_".join(title.split()).lower()


def _is_int(value: str) -> bool:
    try:
        int(value)
    except ValueError:
        return False
    return True


def _is_float(value: str) -> bool:
    try:
        float(value)
    except ValueError:
        return False
    return True


def _is_bool(value: str) -> bool:
    return value.lower() in ("true", "false")


def _placeholder_names(steps: list[Step]) -> list[str]:
    seen: set[str] = set()
    names: list[str] = []
    for step in steps:
        for placeholder in step.placeholders:
            if placeholder.name not in seen:
                seen.add(placeholder.name)
                names.append(placeholder.name)
    return names


def _infer_param_type(name: str, examples: Examples | None) -> str:
    if examples is None:
        return "str"
    values = [row[name] for row in examples.rows if name in row]
    if not values:
        return "str"
    if all(_is_int(v) for v in values):
        return "int"
    if all(_is_float(v) for v in values):
        return "float"
    if all(_is_bool(v) for v in values):
        return "bool"
    return "str"


def _signature_params(scenario: Scenario) -> str:
    parts: list[str] = []
    for name in _placeholder_names(scenario.steps):
        parts.append(f"{name}: {_infer_param_type(name, scenario.examples)}")
    return ", ".join(parts)


def _render_pyi(scenarios: list[Scenario]) -> str:
    lines: list[str] = []
    for scenario in scenarios:
        params = _signature_params(scenario)
        lines.append(f"def {scenario.function_name}({params}) -> None: ...")
    return "\n".join(lines) + "\n"


def _step_block(step: Step) -> str:
    kwargs = "".join(f", {p.name}={p.name}" for p in step.placeholders)
    return f"    with step({step.keyword!r}, {step.text!r}{kwargs}):"


def _render_py(scenarios: list[Scenario]) -> str:
    lines: list[str] = ["from beehave import step"]
    for scenario in scenarios:
        params = _signature_params(scenario)
        lines.append("")
        lines.append("")
        lines.append(f"def {scenario.function_name}({params}) -> None:")
        for step in scenario.steps:
            lines.append(_step_block(step))
            lines.append("        pass")
        if not scenario.steps:
            lines.append("    pass")
    return "\n".join(lines) + "\n"


def _emit_group(
    *,
    tests_dir: Path,
    stem: str,
    scenarios: list[Scenario],
) -> None:
    pyi_path = tests_dir / f"{stem}_test.pyi"
    py_path = tests_dir / f"{stem}_test.py"
    pyi_path.write_text(_render_pyi(scenarios))
    if not py_path.exists():
        py_path.write_text(_render_py(scenarios))


def generate(root: Path) -> None:
    features_dir = root / "docs" / "features"
    tests_dir = root / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)

    for feature_path in sorted(features_dir.glob("*.feature")):
        feature = parse_feature(feature_path.read_text())
        feature_slug = _slug_from(feature_path.stem)

        default_scenarios: list[Scenario] = []
        rules: list[Rule] = []
        for child in feature.children:
            if isinstance(child, Rule):
                rules.append(child)
            else:
                default_scenarios.append(child)

        if default_scenarios:
            _emit_group(
                tests_dir=tests_dir,
                stem=f"{feature_slug}_default",
                scenarios=default_scenarios,
            )
        for rule in rules:
            _emit_group(
                tests_dir=tests_dir,
                stem=f"{feature_slug}_{_slug_from(rule.name)}",
                scenarios=rule.children,
            )
