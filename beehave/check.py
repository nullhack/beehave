from __future__ import annotations

import ast
from typing import TYPE_CHECKING

from beehave.gherkin import Rule, parse_feature

if TYPE_CHECKING:
    from beehave.gherkin import Scenario, Step


def _placeholder_names(steps: list[Step]) -> list[str]:
    seen: set[str] = set()
    names: list[str] = []
    for step in steps:
        for placeholder in step.placeholders:
            if placeholder.name not in seen:
                seen.add(placeholder.name)
                names.append(placeholder.name)
    return names


def _signature_line(scenario: Scenario) -> str:
    names = _placeholder_names(scenario.steps)
    params = ", ".join(f"{name}: str" for name in names)
    return f"def {scenario.function_name}({params}) -> None"


def _expected_signatures(feature_text: str) -> set[str]:
    feature = parse_feature(feature_text)
    sigs: set[str] = set()
    for child in feature.children:
        scenarios = child.children if isinstance(child, Rule) else [child]
        for scenario in scenarios:
            sigs.add(_signature_line(scenario))
    return sigs


def _annotation_str(node: ast.expr | None) -> str:
    if node is None:
        return ""
    return ast.unparse(node)


def _actual_signatures(py_text: str) -> set[str]:
    tree = ast.parse(py_text)
    sigs: set[str] = set()
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        if node.name.startswith("_"):
            continue
        params = ", ".join(
            f"{arg.arg}: {_annotation_str(arg.annotation)}" for arg in node.args.args
        )
        sigs.add(f"def {node.name}({params}) -> None")
    return sigs


def check(feature_text: str, py_text: str) -> bool:
    return _expected_signatures(feature_text) == _actual_signatures(py_text)
