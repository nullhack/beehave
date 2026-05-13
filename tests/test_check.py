from __future__ import annotations

from pathlib import Path

from conftest import write_feature, write_test

from beehave.check import (
    _check_examples_bijection,
    _check_literals,
    _check_placeholders,
    check_all,
    check_pair,
    check_single,
)
from beehave.config import Config
from beehave.generate import generate_stubs
from beehave.models import (
    ExamplesTable,
    Literal,
    Placeholder,
    ScenarioInfo,
    TestInfo,
)


def _make_si(
    title: str = "test scenario",
    function_name: str = "test_test_scenario",
    placeholders: tuple[Placeholder, ...] = (),
    literals: tuple[Literal, ...] = (),
    examples: ExamplesTable | None = None,
    is_outline: bool = False,
    feature_path: str = "feat",
    rule_path: str = "default_test",
    feature_title: str = "Feat",
    line: int = 1,
) -> ScenarioInfo:
    return ScenarioInfo(
        title=title,
        function_name=function_name,
        steps=(),
        placeholders=placeholders,
        literals=literals,
        examples=examples,
        is_outline=is_outline,
        feature_title=feature_title,
        feature_path=feature_path,
        rule_path=rule_path,
        line=line,
    )


def _make_ti(
    function_name: str = "test_test_scenario",
    body_name_nodes: tuple[str, ...] = (),
    body_constant_nodes: tuple[object, ...] = (),
    is_stub: bool = False,
    example_rows: tuple[dict[str, object], ...] = (),
    line: int = 4,
) -> TestInfo:
    return TestInfo(
        function_name=function_name,
        body_name_nodes=body_name_nodes,
        body_constant_nodes=body_constant_nodes,
        is_stub=is_stub,
        example_rows=example_rows,
        line=line,
    )


class TestCheckPlaceholders:
    def test_pass_when_present(self) -> None:
        si = _make_si(placeholders=(Placeholder("x"),))
        ti = _make_ti(body_name_nodes=("x",))
        assert _check_placeholders(si, ti, "test.py") == []

    def test_fail_when_missing(self) -> None:
        si = _make_si(placeholders=(Placeholder("x"),))
        ti = _make_ti(body_name_nodes=())
        v = _check_placeholders(si, ti, "test.py")
        assert len(v) == 1
        assert v[0].error_type == "missing-placeholder"

    def test_stub_skips_check(self) -> None:
        si = _make_si(placeholders=(Placeholder("x"),))
        ti = _make_ti(body_name_nodes=(), is_stub=True)
        assert _check_placeholders(si, ti, "test.py") == []

    def test_only_body_checked_not_given_kwargs(self) -> None:
        si = _make_si(placeholders=(Placeholder("x"),))
        ti = TestInfo(
            function_name="test_test_scenario",
            given_kwargs=("x",),
            body_name_nodes=(),
            is_stub=False,
            line=4,
        )
        v = _check_placeholders(si, ti, "test.py")
        assert len(v) == 1
        assert v[0].error_type == "missing-placeholder"


class TestCheckLiterals:
    def test_pass_when_present(self) -> None:
        si = _make_si(literals=(Literal("hello", '"hello"'),))
        ti = _make_ti(body_constant_nodes=("hello",))
        assert _check_literals(si, ti, "test.py") == []

    def test_fail_when_missing(self) -> None:
        si = _make_si(literals=(Literal("hello", '"hello"'),))
        ti = _make_ti(body_constant_nodes=())
        v = _check_literals(si, ti, "test.py")
        assert len(v) == 1
        assert v[0].error_type == "missing-literal"

    def test_stub_skips_check(self) -> None:
        si = _make_si(literals=(Literal("hello", '"hello"'),))
        ti = _make_ti(body_constant_nodes=(), is_stub=True)
        assert _check_literals(si, ti, "test.py") == []


class TestCheckExamplesBijection:
    def test_matching_rows_pass(self) -> None:
        si = _make_si(
            is_outline=True,
            examples=ExamplesTable(
                headers=("a", "b"),
                rows=(("1", "2"), ("3", "4")),
            ),
        )
        ti = _make_ti(
            example_rows=({"a": 1, "b": 2}, {"a": 3, "b": 4}),
        )
        v = _check_examples_bijection(si, ti, "test.py", "feat.feature")
        assert v == []

    def test_missing_example_row(self) -> None:
        si = _make_si(
            is_outline=True,
            examples=ExamplesTable(
                headers=("a",),
                rows=(("1",), ("2",)),
            ),
        )
        ti = _make_ti(example_rows=({"a": 1},))
        v = _check_examples_bijection(si, ti, "test.py", "feat.feature")
        assert any("Examples row 2" in x.message for x in v)

    def test_extra_example_decorator(self) -> None:
        si = _make_si(
            is_outline=True,
            examples=ExamplesTable(
                headers=("a",),
                rows=(("1",),),
            ),
        )
        ti = _make_ti(example_rows=({"a": 1}, {"a": 2}))
        v = _check_examples_bijection(si, ti, "test.py", "feat.feature")
        assert any("has no matching Examples row" in x.message for x in v)

    def test_non_outline_skips(self) -> None:
        si = _make_si(is_outline=False)
        ti = _make_ti()
        assert _check_examples_bijection(si, ti, "test.py", "feat.feature") == []


class TestCheckPair:
    def test_unmapped_scenario(self) -> None:
        si = _make_si()
        v = check_pair(si, None, "test.py", "feat.feature")
        assert len(v) == 1
        assert v[0].error_type == "unmapped-scenario"

    def test_matching_pair_clean(self) -> None:
        si = _make_si(placeholders=(Placeholder("x"),))
        ti = _make_ti(body_name_nodes=("x",))
        assert check_pair(si, ti, "test.py", "feat.feature") == []


class TestCheckSingle:
    def test_clean_stub_passes(self, tmp_project: Path, config: Config) -> None:
        fp = write_feature(
            tmp_project,
            "clean",
            """\
            Feature: Clean
              Scenario: hello
                Given stuff
            """,
        )
        generate_stubs("clean", config)
        violations = check_single(fp, config)
        assert violations == []

    def test_unmapped_test_detected(self, tmp_project: Path, config: Config) -> None:
        fp = write_feature(
            tmp_project,
            "unmapped",
            """\
            Feature: Unmapped
              Scenario: exists
                Given stuff
            """,
        )
        generate_stubs("unmapped", config)
        write_test(
            tmp_project,
            "unmapped",
            "default_test.py",
            """\
            def test_exists():
                ...

            def test_unmapped_function():
                ...
            """,
        )
        violations = check_single(fp, config)
        types = [v.error_type for v in violations]
        assert "unmapped-test" in types

    def test_missing_placeholder_detected(
        self, tmp_project: Path, config: Config
    ) -> None:
        fp = write_feature(
            tmp_project,
            "ph",
            """\
            Feature: PH Check
              Scenario: check ph
                Given the hive has <amount> nectar
            """,
        )
        generate_stubs("ph", config)
        write_test(
            tmp_project,
            "ph_check",
            "default_test.py",
            """\
            from hypothesis import given, strategies as st

            @given(amount=st.integers())
            def test_check_ph(amount):
                assert True
            """,
        )
        violations = check_single(fp, config)
        types = [v.error_type for v in violations]
        assert "missing-placeholder" in types

    def test_missing_literal_detected(self, tmp_project: Path, config: Config) -> None:
        fp = write_feature(
            tmp_project,
            "lit",
            """\
            Feature: Lit Check
              Scenario: check lit
                Given the bee smells "rose"
            """,
        )
        generate_stubs("lit", config)
        write_test(
            tmp_project,
            "lit_check",
            "default_test.py",
            """\
            def test_check_lit():
                assert True
            """,
        )
        violations = check_single(fp, config)
        types = [v.error_type for v in violations]
        assert "missing-literal" in types

    def test_misplaced_test_after_rule_removal(
        self, tmp_project: Path, config: Config
    ) -> None:
        write_feature(
            tmp_project,
            "mv",
            """\
            Feature: Move
              Scenario: top level
                Given stuff

              Rule: Sub
                Scenario: sub scenario
                  Given things
            """,
        )
        generate_stubs("mv", config)
        write_feature(
            tmp_project,
            "mv",
            """\
            Feature: Move
              Scenario: top level
                Given stuff

              Scenario: sub scenario
                Given things
            """,
        )
        generate_stubs("mv", config)
        fp = tmp_project / "docs" / "features" / "mv.feature"
        violations = check_single(fp, config)
        warnings = [v for v in violations if v.error_type == "misplaced-test"]
        assert len(warnings) >= 1
        assert all(v.is_warning for v in warnings)

    def test_rule_based_files_checked(self, tmp_project: Path, config: Config) -> None:
        fp = write_feature(
            tmp_project,
            "rules",
            """\
            Feature: Rules
              Rule: Alpha
                Scenario: alpha one
                  Given stuff
            """,
        )
        generate_stubs("rules", config)
        violations = check_single(fp, config)
        assert violations == []


class TestCheckAll:
    def test_checks_all_features(self, tmp_project: Path, config: Config) -> None:
        write_feature(
            tmp_project,
            "f1",
            """\
            Feature: F1
              Scenario: s1
                Given stuff
            """,
        )
        write_feature(
            tmp_project,
            "f2",
            """\
            Feature: F2
              Scenario: s2
                Given stuff
            """,
        )
        generate_stubs("f1", config)
        generate_stubs("f2", config)
        violations = check_all(config)
        assert violations == []

    def test_detects_cross_feature_unmapped(
        self, tmp_project: Path, config: Config
    ) -> None:
        write_feature(
            tmp_project,
            "cross",
            """\
            Feature: Cross
              Scenario: cross scenario
                Given stuff
            """,
        )
        generate_stubs("cross", config)
        write_test(
            tmp_project,
            "cross",
            "default_test.py",
            """\
            def test_cross_scenario():
                ...

            def test_unmapped():
                ...
            """,
        )
        violations = check_all(config)
        types = [v.error_type for v in violations]
        assert "unmapped-test" in types

    def test_subdirectory_features_found(
        self, tmp_project: Path, config: Config
    ) -> None:
        write_feature(
            tmp_project,
            "cart/shopping",
            """\
            Feature: Shopping
              Scenario: add item
                Given stuff
            """,
        )
        write_feature(
            tmp_project,
            "smoke",
            """\
            Feature: Smoke
              Scenario: everything is fine
                Given stuff
            """,
        )

        generate_stubs("cart/shopping", config)
        generate_stubs("smoke", config)
        violations = check_all(config)
        assert violations == []
