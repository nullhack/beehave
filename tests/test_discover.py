from __future__ import annotations

from pathlib import Path

import pytest
from conftest import write_test

from beehave.discover import (
    DiscoverError,
    _extract_body_nodes,
    _is_stub_body,
    discover_tests,
)


class TestIsStubBody:
    def test_pass_is_stub(self) -> None:
        import ast

        body = ast.parse("pass").body
        assert _is_stub_body(body) is True

    def test_ellipsis_is_stub(self) -> None:
        import ast

        body = ast.parse("...").body
        assert _is_stub_body(body) is True

    def test_real_code_not_stub(self) -> None:
        import ast

        body = ast.parse("x = 1\ny = 2").body
        assert _is_stub_body(body) is False

    def test_docstring_plus_pass_not_stub(self) -> None:
        import ast

        body = ast.parse('"docstring"\npass').body
        assert _is_stub_body(body) is False


class TestExtractBodyNodes:
    def test_names_extracted(self) -> None:
        import ast

        body = ast.parse("x = y + z").body
        names, _ = _extract_body_nodes(body)
        assert "x" in names
        assert "y" in names
        assert "z" in names

    def test_constants_extracted(self) -> None:
        import ast

        body = ast.parse('x = 42\ny = "hello"').body
        _names, constants = _extract_body_nodes(body)
        assert 42 in constants
        assert "hello" in constants

    def test_leading_docstring_skipped(self) -> None:
        import ast

        body = ast.parse('"This is a docstring"\nx = 1').body
        _names, constants = _extract_body_nodes(body)
        assert 1 in constants

    def test_empty_body(self) -> None:

        body: list = []
        names, constants = _extract_body_nodes(body)
        assert names == ()
        assert constants == ()


class TestDiscoverTests:
    def test_discovers_test_functions(self, tmp_project: Path) -> None:
        p = write_test(
            tmp_project,
            "myfeat",
            "default_test.py",
            """\
            from hypothesis import given, strategies as st

            @given(x=st.integers())
            def test_something(x):
                assert x == x

            def test_plain():
                pass
            """,
        )
        result = discover_tests(p)
        assert "test_something" in result
        assert "test_plain" in result
        assert result["test_something"].given_kwargs == ("x",)
        assert result["test_plain"].given_kwargs == ()

    def test_stub_detection(self, tmp_project: Path) -> None:
        p = write_test(
            tmp_project,
            "stubs",
            "default_test.py",
            """\
            def test_stub():
                ...
            def test_real():
                assert True
            """,
        )
        result = discover_tests(p)
        assert result["test_stub"].is_stub is True
        assert result["test_real"].is_stub is False

    def test_example_rows_extracted(self, tmp_project: Path) -> None:
        p = write_test(
            tmp_project,
            "ex",
            "default_test.py",
            """\
            from hypothesis import example, given, strategies as st

            @example(x=1, y=2)
            @example(x=3, y=4)
            @given(x=st.integers(), y=st.integers())
            def test_outline(x, y):
                ...
            """,
        )
        result = discover_tests(p)
        ti = result["test_outline"]
        assert len(ti.example_rows) == 2
        assert ti.example_rows[0] == {"x": 1, "y": 2}

    def test_body_name_nodes(self, tmp_project: Path) -> None:
        p = write_test(
            tmp_project,
            "names",
            "default_test.py",
            """\
            def test_names(amount):
                result = process(amount)
                assert result
            """,
        )
        result = discover_tests(p)
        ti = result["test_names"]
        assert "amount" in ti.body_name_nodes
        assert "result" in ti.body_name_nodes
        assert "process" in ti.body_name_nodes

    def test_body_constant_nodes(self, tmp_project: Path) -> None:
        p = write_test(
            tmp_project,
            "consts",
            "default_test.py",
            """\
            def test_consts():
                assert "floral" in scents
                assert 42 == count
            """,
        )
        result = discover_tests(p)
        ti = result["test_consts"]
        assert "floral" in ti.body_constant_nodes
        assert 42 in ti.body_constant_nodes

    def test_non_test_functions_ignored(self, tmp_project: Path) -> None:
        p = write_test(
            tmp_project,
            "non",
            "default_test.py",
            """\
            def helper():
                pass
            """,
        )
        result = discover_tests(p)
        assert "helper" not in result

    def test_nonexistent_file_returns_empty(self) -> None:
        result = discover_tests(Path("/nonexistent/file.py"))
        assert result == {}

    def test_syntax_error_raises(self, tmp_project: Path) -> None:
        p = write_test(
            tmp_project,
            "bad",
            "default_test.py",
            "def test_broken(\n",
        )
        with pytest.raises(DiscoverError):
            discover_tests(p)
