from __future__ import annotations

from pathlib import Path

import pytest
from conftest import write_feature
from hypothesis import given, settings
from hypothesis import strategies as st

from beehave.config import Config
from beehave.gherkin import (
    GherkinError,
    _derive_feature_path,
    _derive_function_name,
    _derive_rule_path,
    _extract_literals,
    _extract_placeholders,
    _validate_title,
    parse_feature,
)


class TestValidateTitle:
    def test_empty_raises(self) -> None:
        with pytest.raises(GherkinError, match="non-empty"):
            _validate_title("", "Scenario")

    def test_whitespace_only_raises(self) -> None:
        with pytest.raises(GherkinError, match="non-empty"):
            _validate_title("   ", "Scenario")

    def test_special_chars_raises(self) -> None:
        with pytest.raises(GherkinError, match="invalid characters"):
            _validate_title("hello@world", "Scenario")

    def test_valid_passes(self) -> None:
        _validate_title("simple scenario", "Scenario")

    def test_unicode_letters_pass(self) -> None:
        _validate_title("café résumé", "Scenario")

    @given(st.from_regex(r"[a-zA-Z]\w*", fullmatch=True))
    @settings(max_examples=50)
    def test_valid_titles_never_raise(self, title: str) -> None:
        _validate_title(title, "Scenario")


class TestDeriveFunctionName:
    def test_simple(self) -> None:
        assert _derive_function_name("hello world") == "test_hello_world"

    def test_extra_spaces_collapsed(self) -> None:
        assert _derive_function_name("hello   world") == "test_hello_world"

    def test_leading_trimming(self) -> None:
        assert _derive_function_name("  hello  ") == "test_hello"

    def test_invalid_identifier_raises(self) -> None:
        with pytest.raises(GherkinError, match="not a valid Python identifier"):
            _derive_function_name("hello-world")

    @given(st.from_regex(r"[a-zA-Z_][a-zA-Z0-9_]*", fullmatch=True))
    @settings(max_examples=50)
    def test_single_word_always_valid(self, word: str) -> None:
        result = _derive_function_name(word)
        assert result.startswith("test_")
        assert result.isidentifier()


class TestDeriveFeaturePath:
    def test_simple(self) -> None:
        assert _derive_feature_path("Bank Account") == "bank_account"

    def test_extra_spaces(self) -> None:
        assert _derive_feature_path("Bank   Account") == "bank_account"

    def test_already_lowercase(self) -> None:
        assert _derive_feature_path("bank") == "bank"


class TestDeriveRulePath:
    def test_simple(self) -> None:
        assert _derive_rule_path("Hive Defense") == "hive_defense"

    def test_matches_feature_path_algorithm(self) -> None:
        assert _derive_rule_path("A  B C") == _derive_feature_path("A  B C")


class TestExtractPlaceholders:
    def test_no_placeholders(self) -> None:
        assert _extract_placeholders("hello world") == ()

    def test_single(self) -> None:
        result = _extract_placeholders("has <amount> grams")
        assert len(result) == 1
        assert result[0].name == "amount"

    def test_duplicate_deduped(self) -> None:
        result = _extract_placeholders("<x> and <x> again")
        assert len(result) == 1

    def test_invalid_identifier_raises(self) -> None:
        with pytest.raises(GherkinError, match="not a valid Python identifier"):
            _extract_placeholders("<123bad>")

    def test_keyword_raises(self) -> None:
        with pytest.raises(GherkinError, match="Python keyword"):
            _extract_placeholders("<class>")

    def test_builtin_raises(self) -> None:
        with pytest.raises(GherkinError, match="shadows a Python builtin"):
            _extract_placeholders("<len>")

    @given(
        st.from_regex(r"[a-zA-Z_][a-zA-Z0-9_]*", fullmatch=True).filter(
            lambda s: (
                s
                not in (
                    "len",
                    "str",
                    "int",
                    "float",
                    "bool",
                    "list",
                    "dict",
                    "set",
                    "tuple",
                    "type",
                    "print",
                    "input",
                    "range",
                    "enumerate",
                    "zip",
                    "map",
                    "filter",
                    "sorted",
                    "reversed",
                    "open",
                    "isinstance",
                    "issubclass",
                    "hasattr",
                    "getattr",
                    "setattr",
                    "delattr",
                    "property",
                    "staticmethod",
                    "classmethod",
                    "super",
                    "object",
                    "Exception",
                    "BaseException",
                    "True",
                    "False",
                    "None",
                )
            )
        )
    )
    @settings(max_examples=30)
    def test_valid_identifiers_extracted(self, name: str) -> None:
        import keyword

        if keyword.iskeyword(name):
            with pytest.raises(GherkinError):
                _extract_placeholders(f"<{name}>")
        else:
            result = _extract_placeholders(f"<{name}>")
            assert len(result) == 1
            assert result[0].name == name


class TestExtractLiterals:
    def test_numeric(self) -> None:
        result = _extract_literals("has 100 items")
        assert len(result) == 1
        assert result[0].value == 100

    def test_double_quoted_string(self) -> None:
        result = _extract_literals('named "Alice"')
        assert len(result) == 1
        assert result[0].value == "Alice"
        assert result[0].raw == '"Alice"'

    def test_single_quoted_string(self) -> None:
        result = _extract_literals("named 'Bob'")
        assert len(result) == 1
        assert result[0].value == "Bob"
        assert result[0].raw == "'Bob'"

    def test_both_quote_styles(self) -> None:
        result = _extract_literals("""from 'home' to "work" """)
        assert len(result) == 2
        values = [lit.value for lit in result]
        assert "home" in values
        assert "work" in values

    def test_no_literals(self) -> None:
        assert _extract_literals("plain text here") == ()

    def test_numeric_and_string(self) -> None:
        result = _extract_literals('has 3 items named "foo"')
        assert len(result) == 2


class TestParseFeature:
    def test_simple_scenario(self, tmp_project: Path, config: Config) -> None:
        fp = write_feature(
            tmp_project,
            "simple",
            """\
            Feature: Simple
              Scenario: hello world
                Given something
            """,
        )
        result = parse_feature(fp, config)
        assert "test_hello_world" in result
        si = result["test_hello_world"]
        assert si.title == "hello world"
        assert si.feature_title == "Simple"
        assert si.feature_path == "simple"
        assert si.rule_path == "default_test"

    def test_scenario_outline(self, tmp_project: Path, config: Config) -> None:
        fp = write_feature(
            tmp_project,
            "outline",
            """\
            Feature: Outline Test
              Scenario Outline: addition
                Given <a> and <b>
                Then result is <c>

                Examples:
                  | a | b | c |
                  | 1 | 2 | 3 |
            """,
        )
        result = parse_feature(fp, config)
        si = result["test_addition"]
        assert si.is_outline is True
        assert si.examples is not None
        assert si.examples.rows == (("1", "2", "3"),)

    def test_background_merged(self, tmp_project: Path, config: Config) -> None:
        fp = write_feature(
            tmp_project,
            "bg",
            """\
            Feature: Background Test
              Background:
                Given the system is ready

              Scenario: do something
                Given a user exists
            """,
        )
        result = parse_feature(fp, config)
        si = result["test_do_something"]
        names = [ph.name for ph in si.placeholders]
        assert "system" not in names

    def test_background_no_placeholders(
        self, tmp_project: Path, config: Config
    ) -> None:
        fp = write_feature(
            tmp_project,
            "bgph",
            """\
            Feature: Bad Background
              Background:
                Given the hive has <amount> nectar

              Scenario: something
                Given stuff
            """,
        )
        with pytest.raises(GherkinError, match="placeholder"):
            parse_feature(fp, config)

    def test_rule_creates_separate_rule_path(
        self, tmp_project: Path, config: Config
    ) -> None:
        fp = write_feature(
            tmp_project,
            "rules",
            """\
            Feature: Rule Test
              Scenario: top level

              Rule: My Rule
                Scenario: inside rule
            """,
        )
        result = parse_feature(fp, config)
        assert result["test_top_level"].rule_path == "default_test"
        assert result["test_inside_rule"].rule_path == "my_rule_test"

    def test_global_function_name_collision(
        self, tmp_project: Path, config: Config
    ) -> None:
        fp1 = write_feature(
            tmp_project,
            "f1",
            """\
            Feature: Feature One
              Scenario: same name
                Given stuff
            """,
        )
        fp2 = write_feature(
            tmp_project,
            "f2",
            """\
            Feature: Feature Two
              Scenario: same name
                Given stuff
            """,
        )
        parse_feature(fp1, config)
        with pytest.raises(GherkinError, match="collides"):
            parse_feature(
                fp2, config, seen_function_names={"test_same_name": "Feature One"}
            )

    def test_feature_not_found(self, tmp_project: Path, config: Config) -> None:
        with pytest.raises(GherkinError, match="not found"):
            parse_feature(tmp_project / "nonexistent.feature", config)

    def test_literal_extraction_from_steps(
        self, tmp_project: Path, config: Config
    ) -> None:
        fp = write_feature(
            tmp_project,
            "lits",
            """\
            Feature: Literal Test
              Scenario: literal check
                Given the bee has 3 wings and "honey" scent
            """,
        )
        result = parse_feature(fp, config)
        si = result["test_literal_check"]
        values = [lit.value for lit in si.literals]
        assert 3 in values
        assert "honey" in values

    def test_background_literals_enforced_by_default(
        self, tmp_project: Path, config: Config
    ) -> None:
        fp = write_feature(
            tmp_project,
            "bglit",
            """\
            Feature: BG Literals
              Background:
                Given the entrance has 2 guards
                And the hive is "active"

              Scenario: check guards
                Given a visitor arrives
            """,
        )
        result = parse_feature(fp, config)
        si = result["test_check_guards"]
        values = [lit.value for lit in si.literals]
        assert 2 in values
        assert "active" in values

    def test_background_literals_configurable(self, tmp_project: Path) -> None:
        cfg = Config(
            features_dir=str(tmp_project / "docs" / "features"),
            tests_dir=str(tmp_project / "tests" / "features"),
            background_check_numeric=False,
            background_check_string=False,
        )
        fp = write_feature(
            tmp_project,
            "bgconf",
            """\
            Feature: BG Config
              Background:
                Given the entrance has 2 guards
                And the hive is "active"

              Scenario: check
                Given a visitor
            """,
        )
        result = parse_feature(fp, cfg)
        si = result["test_check"]
        assert all(not isinstance(lit.value, int) for lit in si.literals)
        assert all(not isinstance(lit.value, str) for lit in si.literals)

    def test_rule_background_composes(self, tmp_project: Path, config: Config) -> None:
        fp = write_feature(
            tmp_project,
            "rulebg",
            """\
            Feature: Rule BG
              Background:
                Given feature bg

              Rule: Sub
                Background:
                  Given rule bg with "special"

                Scenario: combined
                  Given scenario step
            """,
        )
        result = parse_feature(fp, config)
        si = result["test_combined"]
        values = [lit.value for lit in si.literals]
        assert "special" in values
