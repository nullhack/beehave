from __future__ import annotations

from pathlib import Path

import pytest
from conftest import write_feature
from hypothesis import given, settings
from hypothesis import strategies as st

from beehave.config import Config
from beehave.generate import (
    _build_import_block,
    _generate_function,
    _infer_strategy_from_examples,
    _parse_existing_imports,
    generate_stubs,
)
from beehave.models import (
    ExamplesTable,
    Placeholder,
    ScenarioInfo,
    coerce_example_value,
)


def _make_si(
    title: str = "test scenario",
    function_name: str = "test_test_scenario",
    placeholders: tuple[Placeholder, ...] = (),
    examples: ExamplesTable | None = None,
    is_outline: bool = False,
    feature_path: str = "feat",
    rule_path: str = "default_test",
    feature_title: str = "Feat",
) -> ScenarioInfo:
    return ScenarioInfo(
        title=title,
        function_name=function_name,
        steps=(),
        placeholders=placeholders,
        literals=(),
        examples=examples,
        is_outline=is_outline,
        feature_title=feature_title,
        feature_path=feature_path,
        rule_path=rule_path,
    )


class TestCoerceExampleValue:
    def test_integer(self) -> None:
        assert coerce_example_value("42") == 42

    def test_negative_integer(self) -> None:
        assert coerce_example_value("-5") == -5

    def test_float(self) -> None:
        result = coerce_example_value("3.14")
        assert isinstance(result, float)
        assert abs(result - 3.14) < 1e-10

    def test_true(self) -> None:
        assert coerce_example_value("true") is True

    def test_false(self) -> None:
        assert coerce_example_value("false") is False

    def test_quoted_string(self) -> None:
        assert coerce_example_value('"hello"') == "hello"

    def test_plain_text(self) -> None:
        assert coerce_example_value("hello") == "hello"

    @given(st.integers(min_value=-1000, max_value=1000))
    @settings(max_examples=50)
    def test_integer_roundtrip(self, n: int) -> None:
        assert coerce_example_value(str(n)) == n

    @given(st.from_regex(r"-?\d+\.\d+", fullmatch=True))
    @settings(max_examples=30)
    def test_float_detection(self, s: str) -> None:
        result = coerce_example_value(s)
        assert isinstance(result, float)


class TestInferStrategy:
    def test_all_integers(self) -> None:
        table = ExamplesTable(headers=("x",), rows=(("1",), ("2",), ("3",)))
        assert _infer_strategy_from_examples("x", table) == "st.integers()"

    def test_all_floats(self) -> None:
        table = ExamplesTable(headers=("x",), rows=(("1.0",), ("2.5",)))
        assert _infer_strategy_from_examples("x", table) == "st.floats()"

    def test_all_booleans(self) -> None:
        table = ExamplesTable(headers=("x",), rows=(("true",), ("false",)))
        assert _infer_strategy_from_examples("x", table) == "st.booleans()"

    def test_mixed_defaults_to_text(self) -> None:
        table = ExamplesTable(headers=("x",), rows=(("1",), ("hello",)))
        assert _infer_strategy_from_examples("x", table) == "st.text()"


class TestBuildImportBlock:
    def test_no_placeholders_no_import(self) -> None:
        scenarios = {"test_a": _make_si(placeholders=())}
        assert _build_import_block(scenarios) == []

    def test_with_placeholders(self) -> None:
        scenarios = {"test_a": _make_si(placeholders=(Placeholder("x"),))}
        block = _build_import_block(scenarios)
        assert len(block) == 2
        assert "from hypothesis import given, strategies as st" in block[0]

    def test_with_outline(self) -> None:
        scenarios = {
            "test_a": _make_si(
                is_outline=True,
                examples=ExamplesTable(headers=("x",), rows=(("1",),)),
            )
        }
        block = _build_import_block(scenarios)
        assert any("example" in line for line in block)


class TestGenerateFunction:
    def test_simple_function(self) -> None:
        si = _make_si(
            function_name="test_simple",
            placeholders=(Placeholder("x"),),
        )
        result = _generate_function(si, set(), Config())
        assert "def test_simple(x):" in result
        assert "@given(x=st.text())" in result
        assert "    ..." in result

    def test_no_params(self) -> None:
        si = _make_si(function_name="test_plain", placeholders=())
        result = _generate_function(si, set(), Config())
        assert "def test_plain():" in result
        assert "@given" not in result

    def test_outline_generates_examples(self) -> None:
        si = _make_si(
            function_name="test_outline",
            placeholders=(Placeholder("a"), Placeholder("b")),
            is_outline=True,
            examples=ExamplesTable(
                headers=("a", "b"),
                rows=(("1", "2"), ("3", "4")),
            ),
        )
        result = _generate_function(si, set(), Config())
        assert "@example(a=1, b=2)" in result
        assert "@example(a=3, b=4)" in result


class TestParseExistingImports:
    def test_extracts_hypothesis_imports(self) -> None:
        source = "from hypothesis import given, strategies as st\n"
        result = _parse_existing_imports(source)
        assert "given" in result
        assert "st" in result

    def test_non_hypothesis_ignored(self) -> None:
        source = "from os import path\n"
        result = _parse_existing_imports(source)
        assert result == set()


class TestGenerateStubs:
    def test_creates_default_test(self, tmp_project: Path, config: Config) -> None:
        write_feature(
            tmp_project,
            "gen1",
            """\
            Feature: Gen1
              Scenario: hello
                Given stuff
            """,
        )
        generate_stubs("gen1", config)
        test_file = tmp_project / "tests" / "features" / "gen1" / "default_test.py"
        assert test_file.exists()
        content = test_file.read_text()
        assert "def test_hello():" in content

    def test_creates_rule_files(self, tmp_project: Path, config: Config) -> None:
        write_feature(
            tmp_project,
            "gen2",
            """\
            Feature: Gen2
              Scenario: top

              Rule: My Rule
                Scenario: in rule
                  Given stuff
            """,
        )
        generate_stubs("gen2", config)
        default = tmp_project / "tests" / "features" / "gen2" / "default_test.py"
        rule = tmp_project / "tests" / "features" / "gen2" / "my_rule_test.py"
        assert default.exists()
        assert rule.exists()
        assert "def test_top():" in default.read_text()
        assert "def test_in_rule():" in rule.read_text()

    def test_idempotent(self, tmp_project: Path, config: Config) -> None:
        write_feature(
            tmp_project,
            "idem",
            """\
            Feature: Idem
              Scenario: once
                Given stuff
            """,
        )
        generate_stubs("idem", config)
        first = (
            tmp_project / "tests" / "features" / "idem" / "default_test.py"
        ).read_text()
        generate_stubs("idem", config)
        second = (
            tmp_project / "tests" / "features" / "idem" / "default_test.py"
        ).read_text()
        assert first == second

    def test_scenario_outline_with_examples(
        self, tmp_project: Path, config: Config
    ) -> None:
        write_feature(
            tmp_project,
            "outline",
            """\
            Feature: Outline
              Scenario Outline: addition
                Given <a> and <b>

                Examples:
                  | a | b |
                  | 1 | 2 |
            """,
        )
        generate_stubs("outline", config)
        content = (
            tmp_project / "tests" / "features" / "outline" / "default_test.py"
        ).read_text()
        assert "@example(a=1, b=2)" in content
        assert "@given(a=st.integers(), b=st.integers())" in content

    def test_nonexistent_feature_exits(self, tmp_project: Path, config: Config) -> None:
        with pytest.raises(SystemExit):
            generate_stubs("nonexistent", config)
