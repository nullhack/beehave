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

PLAIN_FEATURE_WITH_ANGLE = """\
Feature: Parametrize Emission
Scenario: plain angles
Given a step with <not_a_param> in text
Then anything
"""

MULTI_TABLE_FEATURE = """\
Feature: Parametrize Emission
Scenario Outline: honey from nectar
Given the hive has <nectar> grams
Then the hive produces <honey> grams

Examples:
  | nectar | honey |
  | 100    | 80    |

Examples:
  | nectar | honey |
  | 200    | 150   |
"""

DIFFERENT_TAG_TABLES_FEATURE = """\
Feature: Parametrize Emission
Scenario Outline: honey from nectar
Given the hive has <nectar> grams
Then the hive produces <honey> grams

@slow
Examples:
  | nectar | honey |
  | 1000   | 800   |

@fast
Examples:
  | nectar | honey |
  | 10     | 8     |
"""


def _emitted_py(feature_text: str) -> str:
    from beehave.generate import generate

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        features = root / "docs" / "features"
        features.mkdir(parents=True)
        (features / "input.feature").write_text(feature_text)
        generate(root)
        return (root / "tests" / "features" / "input_default_test.py").read_text()


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


def test_plain_scenario_treats_angle_as_literal_text() -> None:
    py = _emitted_py(PLAIN_FEATURE_WITH_ANGLE)
    assert "<not_a_param>" in py
    assert "def test_plain_angles() -> None:" in py


def test_multiple_examples_tables_are_merged() -> None:
    py = _emitted_py(MULTI_TABLE_FEATURE)
    assert "('100', '80')," in py
    assert "('200', '150')," in py


def test_different_tagged_tables_emit_pytest_param() -> None:
    py = _emitted_py(DIFFERENT_TAG_TABLES_FEATURE)
    assert "pytest.param('1000', '800', marks=pytest.mark.slow)" in py
    assert "pytest.param('10', '8', marks=pytest.mark.fast)" in py


def test_check_passes_on_freshly_generated_py() -> None:
    from beehave.check import check

    py = _emitted_py(OUTLINE_FEATURE)
    assert check(OUTLINE_FEATURE, py)
