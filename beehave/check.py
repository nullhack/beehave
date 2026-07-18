from __future__ import annotations

import ast
from typing import TYPE_CHECKING

from beehave.gherkin import Rule, parse_feature

if TYPE_CHECKING:
    from beehave.gherkin import Examples, Scenario, Step


def _step_block_from_item(
    item: ast.withitem,
) -> tuple[str, str, set[str]] | None:
    call = item.context_expr
    if not isinstance(call, ast.Call):
        return None
    callee = call.func
    if not isinstance(callee, ast.Name) or callee.id != "step":
        return None
    if len(call.args) < 2:
        return None
    try:
        keyword = ast.literal_eval(call.args[0])
        text = ast.literal_eval(call.args[1])
    except ValueError, SyntaxError:
        return None
    if not isinstance(keyword, str) or not isinstance(text, str):
        return None
    names = {kw.arg for kw in call.keywords if kw.arg is not None}
    return (keyword, text, names)


def _step_blocks(
    function: ast.FunctionDef,
) -> list[tuple[str, str, set[str]]]:
    blocks: list[tuple[str, str, set[str]]] = []
    for stmt in function.body:
        if not isinstance(stmt, ast.With):
            continue
        for item in stmt.items:
            block = _step_block_from_item(item)
            if block is not None:
                blocks.append(block)
    return blocks


def _parametrize_of(
    function: ast.FunctionDef,
) -> tuple[list[str], list[tuple[str, ...]]] | None:
    for decorator in function.decorator_list:
        if not isinstance(decorator, ast.Call):
            continue
        func = decorator.func
        if (
            not isinstance(func, ast.Attribute)
            or func.attr != "parametrize"
            or not isinstance(func.value, ast.Attribute)
            or func.value.attr != "mark"
            or not isinstance(func.value.value, ast.Name)
            or func.value.value.id != "pytest"
        ):
            continue
        if len(decorator.args) < 2:
            continue
        try:
            arg_names = ast.literal_eval(decorator.args[0])
            rows = ast.literal_eval(decorator.args[1])
        except ValueError, SyntaxError:
            continue
        if not isinstance(arg_names, tuple) or not isinstance(rows, list):
            continue
        return (list(arg_names), [tuple(r) for r in rows])
    return None


def _examples_rows(
    scenario: Scenario,
) -> tuple[list[str], list[tuple[str, ...]]] | None:
    examples: Examples | None = scenario.examples
    if examples is None:
        return None
    headers = list(examples.headers)
    rows = [tuple(row[h] for h in headers) for row in examples.rows]
    return (headers, rows)


def _step_matches(
    block: tuple[str, str, set[str]],
    step: Step,
) -> bool:
    keyword, text, names = block
    if keyword.lower() != step.keyword.lower():
        return False
    if text != step.text:
        return False
    return names == {p.name for p in step.placeholders}


def _scenario_matches(
    scenario: Scenario,
    blocks_by_function: dict[str, list[tuple[str, str, set[str]]]],
    parametrize_by_function: dict[str, tuple[list[str], list[tuple[str, ...]]] | None],
) -> bool:
    name = scenario.function_name
    blocks = blocks_by_function.get(name, [])
    if len(blocks) != len(scenario.steps):
        return False
    if not all(
        _step_matches(block, step)
        for block, step in zip(blocks, scenario.steps, strict=True)
    ):
        return False
    expected = _examples_rows(scenario)
    if expected is not None:
        actual = parametrize_by_function.get(name)
        if actual is None or actual != expected:
            return False
    return True


def check(feature_text: str, test_py_text: str) -> bool:
    feature = parse_feature(feature_text)
    try:
        tree = ast.parse(test_py_text)
    except SyntaxError:
        return False
    blocks_by_function: dict[str, list[tuple[str, str, set[str]]]] = {}
    parametrize_by_function: dict[
        str, tuple[list[str], list[tuple[str, ...]]] | None
    ] = {}
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        blocks_by_function[node.name] = _step_blocks(node)
        parametrize_by_function[node.name] = _parametrize_of(node)
    for child in feature.children:
        scenarios = child.children if isinstance(child, Rule) else [child]
        for scenario in scenarios:
            if not _scenario_matches(
                scenario, blocks_by_function, parametrize_by_function
            ):
                return False
    return True
