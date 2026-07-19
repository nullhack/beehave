from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from beehave.gherkin import Rule, parse_feature

if TYPE_CHECKING:
    from beehave.gherkin import DataTable, Examples, Scenario, Step


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
    distinct_tags = {tuple(tags) for tags in examples.row_tags}
    use_param = len(distinct_tags) > 1
    lines = [
        "@pytest.mark.parametrize(",
        f"    ({arg_names}),",
        "    [",
    ]
    for row, tags in zip(examples.rows, examples.row_tags, strict=False):
        cells = ", ".join(repr(row[h]) for h in examples.headers)
        if use_param and tags:
            marks = ", ".join(f"pytest.mark.{t}" for t in tags)
            lines.append(f"        pytest.param({cells}, marks={marks}),")
        else:
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


def _data_table_repr(dt: DataTable) -> str:
    if dt.headers is None:
        return repr(dt.rows)
    items: list[str] = []
    for row in dt.rows:
        pairs = ", ".join(
            f"{h!r}: {v!r}" for h, v in zip(dt.headers, row, strict=False)
        )
        items.append("{" + pairs + "}")
    return "[" + ", ".join(items) + "]"


def _step_body_lines(step: Step) -> list[str]:
    lines: list[str] = []
    if step.docstring is not None:
        lines.append(f"        docstring = {step.docstring!r}")
    if step.data_table is not None:
        lines.append(f"        data_table = {_data_table_repr(step.data_table)}")
    if not lines:
        lines.append("        pass")
    return lines


def _render_py(scenarios: list[Scenario], module_tags: list[str]) -> str:
    lines: list[str] = ["from beehave import step", "import pytest"]
    if module_tags:
        marks = ", ".join(f"pytest.mark.{t}" for t in module_tags)
        lines.append(f"pytestmark = [{marks}]")
    for scenario in scenarios:
        params = _signature_params(scenario)
        lines.append("")
        lines.append("")
        for tag in scenario.tags:
            lines.append(f"@pytest.mark.{tag}")
        lines.extend(_parametrize_lines(scenario))
        lines.append(f"def {scenario.function_name}({params}) -> None:")
        for step in scenario.steps:
            lines.append(_step_block(step))
            lines.extend(_step_body_lines(step))
        if not scenario.steps:
            lines.append("    pass")
    return "\n".join(lines) + "\n"


def _emit_group(
    *,
    tests_dir: Path,
    stem: str,
    scenarios: list[Scenario],
    module_tags: list[str],
) -> None:
    pyi_path = tests_dir / f"{stem}_test.pyi"
    py_path = tests_dir / f"{stem}_test.py"
    pyi_path.write_text(_render_pyi(scenarios))
    if not py_path.exists():
        py_path.write_text(_render_py(scenarios, module_tags))


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
                module_tags=feature.tags,
            )
        for rule in rules:
            _emit_group(
                tests_dir=tests_dir,
                stem=f"{feature_slug}_{_slug_from(rule.name)}",
                scenarios=rule.children,
                module_tags=[*feature.tags, *rule.tags],
            )
