from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from beehave.gherkin import Rule, parse_feature

if TYPE_CHECKING:
    from beehave.gherkin import Examples, Scenario, Step


def _slug_from(title: str) -> str:
    return "_".join(title.split()).lower()


def _placeholder_names(steps: list[Step]) -> list[str]:
    seen: set[str] = set()
    names: list[str] = []
    for step in steps:
        for placeholder in step.placeholders:
            if placeholder.name not in seen:
                seen.add(placeholder.name)
                names.append(placeholder.name)
    return names


def _signature_params(scenario: Scenario) -> str:
    return ", ".join(f"{name}: str" for name in _placeholder_names(scenario.steps))


def _parametrize_lines(scenario: Scenario) -> list[str]:
    examples: Examples | None = scenario.examples
    if examples is None:
        return []
    arg_names = ", ".join(repr(h) for h in examples.headers)
    lines = [
        "@pytest.mark.parametrize(",
        f"    ({arg_names}),",
        "    [",
    ]
    for row in examples.rows:
        cells = ", ".join(repr(row[h]) for h in examples.headers)
        lines.append(f"        ({cells}),")
    lines.append("    ],")
    lines.append(")")
    return lines


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
    if any(s.examples is not None for s in scenarios):
        lines.append("import pytest")
    for scenario in scenarios:
        params = _signature_params(scenario)
        lines.append("")
        lines.append("")
        lines.extend(_parametrize_lines(scenario))
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
    tests_dir = root / "tests" / "features"
    tests_dir.mkdir(parents=True, exist_ok=True)
    for stale in tests_dir.glob("*_test.pyi"):
        stale.unlink()

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
