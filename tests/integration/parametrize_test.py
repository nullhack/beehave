from __future__ import annotations

import tempfile
from pathlib import Path

OUTLINE_FEATURE = """\
Feature: Parametrize Emission
Scenario Outline: honey from nectar
Given the hive has <nectar> grams
When the bees fan for <hours> hours
Then the hive produces <honey> grams

Examples:
  | nectar | hours | honey |
  | 100    | 8     | 80    |
  | 200    | 12    | 150   |
"""

PLAIN_FEATURE = """\
Feature: Parametrize Emission
Scenario: plain scenario
Given a step
Then anything
"""


def _emit(root: Path, feature_text: str) -> tuple[str, str]:
    from beehave.generate import generate

    features = root / "docs" / "features"
    features.mkdir(parents=True)
    (features / "input.feature").write_text(feature_text)
    generate(root)
    py = (root / "tests" / "features" / "input_default_test.py").read_text()
    pyi = (root / "tests" / "features" / "input_default_test.pyi").read_text()
    return py, pyi


def _emitted_py(feature_text: str) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        py, _pyi = _emit(Path(tmp), feature_text)
    return py


def _emitted_pyi(feature_text: str) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        _py, pyi = _emit(Path(tmp), feature_text)
    return pyi


def _check_result(feature_text: str, test_py_text: str) -> bool:
    from beehave.check import check

    return check(feature_text, test_py_text)


def test_examples_scenario_emits_parametrize_decorator() -> None:
    py = _emitted_py(OUTLINE_FEATURE)
    assert "@pytest.mark.parametrize(" in py


def test_parametrize_arg_names_match_examples_headers() -> None:
    py = _emitted_py(OUTLINE_FEATURE)
    needle = py[py.find("@pytest.mark.parametrize(") :]
    assert "'nectar'" in needle
    assert "'hours'" in needle
    assert "'honey'" in needle


def test_parametrize_rows_match_examples_rows() -> None:
    py = _emitted_py(OUTLINE_FEATURE)
    assert "('100', '8', '80')," in py
    assert "('200', '12', '150')," in py


def test_no_examples_scenario_emits_no_parametrize() -> None:
    py = _emitted_py(PLAIN_FEATURE)
    assert "parametrize" not in py
    assert "import pytest" not in py


def test_pyi_signature_carries_str_params_for_outline() -> None:
    pyi = _emitted_pyi(OUTLINE_FEATURE)
    assert (
        "def test_honey_from_nectar(nectar: str, hours: str, honey: str) -> None:"
        in pyi
    )


def test_check_passes_when_parametrize_matches_examples() -> None:
    py = _emitted_py(OUTLINE_FEATURE)
    assert _check_result(OUTLINE_FEATURE, py)


def test_check_fails_when_examples_present_but_no_parametrize() -> None:
    body_without_parametrize = (
        "from beehave import step\n"
        "\n"
        "def test_honey_from_nectar(nectar: str, hours: str, honey: str) -> None:\n"
        '    with step("Given", "the hive has <nectar> grams", nectar=nectar):\n'
        "        pass\n"
        '    with step("When", "the bees fan for <hours> hours", hours=hours):\n'
        "        pass\n"
        '    with step("Then", "the hive produces <honey> grams", honey=honey):\n'
        "        pass\n"
    )
    assert not _check_result(OUTLINE_FEATURE, body_without_parametrize)


def test_check_fails_when_parametrize_rows_differ() -> None:
    py = _emitted_py(OUTLINE_FEATURE)
    edited = py.replace("('100', '8', '80'),", "('999', '8', '80'),")
    assert edited != py
    assert not _check_result(OUTLINE_FEATURE, edited)


def test_check_fails_when_parametrize_arg_names_differ() -> None:
    py = _emitted_py(OUTLINE_FEATURE)
    edited = py.replace("'nectar'", "'renamed'", 1)
    assert edited != py
    assert not _check_result(OUTLINE_FEATURE, edited)
