"""Verify a generated `_test.py` still matches its `.feature` source."""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING

from beehave.gherkin import Rule, parse_feature

if TYPE_CHECKING:
    from beehave.gherkin import Scenario, Step


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
) -> bool:
    blocks = blocks_by_function.get(scenario.function_name, [])
    if len(blocks) != len(scenario.steps):
        return False
    return all(
        _step_matches(block, step)
        for block, step in zip(blocks, scenario.steps, strict=True)
    )


def check(feature_text: str, test_py_text: str) -> bool:
    """Return True iff every scenario matches a `def` one-to-one.

    Each scenario in `feature_text` must have a `def` in `test_py_text` whose
    `with step(...)` blocks line up on keyword, text, and placeholder names.
    A syntactically invalid test_py_text returns False rather than raising.
    """
    feature = parse_feature(feature_text)
    try:
        tree = ast.parse(test_py_text)
    except SyntaxError:
        return False
    blocks_by_function = {
        node.name: _step_blocks(node)
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
    }
    for child in feature.children:
        scenarios = child.children if isinstance(child, Rule) else [child]
        for scenario in scenarios:
            if not _scenario_matches(scenario, blocks_by_function):
                return False
    return True
