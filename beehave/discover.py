from __future__ import annotations

import ast
from pathlib import Path

from beehave.models import TestInfo


class DiscoverError(Exception):
    pass


def _is_stub_body(body: list[ast.stmt]) -> bool:
    if len(body) == 1:
        node = body[0]
        if isinstance(node, ast.Pass):
            return True
        if (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and node.value.value is ...
        ):
            return True
    return False


def _extract_body_nodes(
    body: list[ast.stmt],
) -> tuple[tuple[str, ...], tuple[object, ...]]:
    check_nodes: list[ast.stmt] = []
    for node in body:
        if (
            not check_nodes
            and isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            continue
        check_nodes.append(node)

    names: set[str] = set()
    constants: set[object] = set()

    for node in ast.walk(ast.Module(body=check_nodes, type_ignores=[])):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Constant):
            constants.add(node.value)

    return tuple(sorted(names)), tuple(sorted(constants, key=repr))


def _extract_given_kwargs(
    decorators: list[ast.expr],
) -> tuple[str, ...]:
    kwargs: list[str] = []
    for dec in decorators:
        if (
            isinstance(dec, ast.Call)
            and isinstance(dec.func, ast.Attribute)
            and dec.func.attr == "given"
        ):
            for kw in dec.keywords:
                if kw.arg:
                    kwargs.append(kw.arg)
    return tuple(kwargs)


def _extract_example_rows(
    decorators: list[ast.expr],
) -> tuple[dict[str, object], ...]:
    rows: list[dict[str, object]] = []
    for dec in decorators:
        if (
            isinstance(dec, ast.Call)
            and isinstance(dec.func, ast.Name)
            and dec.func.id == "example"
        ):
            row: dict[str, object] = {}
            for kw in dec.keywords:
                if kw.arg and isinstance(kw.value, ast.Constant):
                    row[kw.arg] = kw.value.value
            rows.append(row)
    return tuple(rows)


def _discover_module_strategies(tree: ast.Module) -> set[str]:
    strategies: set[str] = set()
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
        ):
            strategies.add(node.targets[0].id)
    return strategies


def discover_tests(test_file: Path) -> dict[str, TestInfo]:
    if not test_file.exists():
        return {}

    try:
        source = test_file.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(test_file))
    except SyntaxError as e:
        raise DiscoverError(f"{test_file}:{e.lineno}: {e.msg}") from e

    _discover_module_strategies(tree)

    result: dict[str, TestInfo] = {}

    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        if not node.name.startswith("test_"):
            continue

        decorators = list(node.decorator_list)
        given_kwargs = _extract_given_kwargs(decorators)
        example_rows = _extract_example_rows(decorators)
        is_stub = _is_stub_body(node.body)
        body_names, body_constants = _extract_body_nodes(node.body)

        result[node.name] = TestInfo(
            function_name=node.name,
            given_kwargs=given_kwargs,
            example_rows=example_rows,
            body_name_nodes=body_names,
            body_constant_nodes=body_constants,
            is_stub=is_stub,
            line=node.lineno,
        )

    return result


def discover_tests_dir(tests_dir: Path) -> dict[str, TestInfo]:
    all_tests: dict[str, TestInfo] = {}
    if not tests_dir.exists():
        return all_tests
    for py_file in tests_dir.rglob("*.py"):
        try:
            tests = discover_tests(py_file)
            all_tests.update(tests)
        except DiscoverError:
            continue
    return all_tests
