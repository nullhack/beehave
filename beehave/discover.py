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
    """Walk a test function body and collect all names and constants.

    The first statement in a multi-statement body is skipped if it is a
    docstring.  ``UnaryOp`` nodes wrapping constants are folded (e.g.
    ``-5`` becomes the constant ``-5``, not ``5`` with a negation flag).

    Args:
        body: The list of AST statements in the function body.

    Returns:
        A 2-tuple of ``(names, constants)``, each sorted.

    """
    check_nodes: list[ast.stmt] = []
    for node in body:
        if (
            not check_nodes
            and isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
            and len(body) > 1
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
        elif isinstance(node, ast.UnaryOp) and isinstance(node.operand, ast.Constant):
            if isinstance(node.op, ast.USub):
                constants.add(-node.operand.value)
            elif isinstance(node.op, ast.UAdd):
                constants.add(node.operand.value)

    return tuple(sorted(names)), tuple(sorted(constants, key=repr))


def _extract_given_kwargs(
    decorators: list[ast.expr],
) -> tuple[str, ...]:
    kwargs: list[str] = []
    for dec in decorators:
        if not isinstance(dec, ast.Call):
            continue
        is_given = (
            isinstance(dec.func, ast.Attribute) and dec.func.attr == "given"
        ) or (isinstance(dec.func, ast.Name) and dec.func.id == "given")
        if is_given:
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


def discover_tests(test_file: Path) -> dict[str, TestInfo]:
    if not test_file.exists():
        return {}

    try:
        source = test_file.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(test_file))
    except SyntaxError as e:
        raise DiscoverError(f"{test_file}:{e.lineno}: {e.msg}") from e

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


def discover_tests_dir_with_paths(
    tests_dir: Path,
) -> dict[str, tuple[TestInfo, Path]]:
    all_tests: dict[str, tuple[TestInfo, Path]] = {}
    if not tests_dir.exists():
        return all_tests
    for py_file in tests_dir.rglob("*_test.py"):
        try:
            tests = discover_tests(py_file)
            for fn, ti in tests.items():
                all_tests[fn] = (ti, py_file)
        except DiscoverError:
            continue
    return all_tests
