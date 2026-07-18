from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

INT_COLUMN_FEATURE = """\
Feature: Strategy Inference
Scenario Outline: int column
Given a value of <amount>
Then anything

Examples:
  | amount |
  | 1      |
  | 2      |
"""

FLOAT_COLUMN_FEATURE = """\
Feature: Strategy Inference
Scenario Outline: float column
Given a value of <amount>
Then anything

Examples:
  | amount |
  | 1.5    |
  | 2.5    |
"""

BOOL_COLUMN_FEATURE = """\
Feature: Strategy Inference
Scenario Outline: bool column
Given a flag of <flag>
Then anything

Examples:
  | flag  |
  | true  |
  | false |
"""

MIXED_COLUMN_FEATURE = """\
Feature: Strategy Inference
Scenario Outline: mixed column
Given a value of <amount>
Then anything

Examples:
  | amount |
  | 1      |
  | 2.5    |
  | hello  |
"""

TEXT_COLUMN_FEATURE = """\
Feature: Strategy Inference
Scenario Outline: text column
Given a value of <name>
Then anything

Examples:
  | name  |
  | alice |
  | bob   |
"""

NO_EXAMPLES_FEATURE = """\
Feature: Strategy Inference
Scenario: no examples
Given a value of <name>
Then anything
"""


def emitted_function_signature(feature_text: str, scenario_slug: str) -> str:
    from beehave.generate import generate

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        features = root / "docs" / "features"
        features.mkdir(parents=True)
        (features / "input.feature").write_text(feature_text)
        generate(root)
        pyi = (root / "tests" / "input_default_test.pyi").read_text()
    needle = f"def test_{scenario_slug}"
    start = pyi.find(needle)
    if start == -1:
        return ""
    end = pyi.find("...", start)
    if end == -1:
        return pyi[start:]
    return pyi[start : end + 3]


@pytest.mark.pending
def test_all_int_column_infers_int_parameter() -> None:
    signature = emitted_function_signature(INT_COLUMN_FEATURE, "int_column")
    assert "amount: int" in signature


@pytest.mark.pending
def test_all_float_column_infers_float_parameter() -> None:
    signature = emitted_function_signature(FLOAT_COLUMN_FEATURE, "float_column")
    assert "amount: float" in signature


@pytest.mark.pending
def test_all_bool_column_infers_bool_parameter() -> None:
    signature = emitted_function_signature(BOOL_COLUMN_FEATURE, "bool_column")
    assert "flag: bool" in signature


@pytest.mark.pending
def test_mixed_type_column_infers_str_parameter() -> None:
    signature = emitted_function_signature(MIXED_COLUMN_FEATURE, "mixed_column")
    assert "amount: str" in signature


@pytest.mark.pending
def test_text_column_infers_str_parameter() -> None:
    signature = emitted_function_signature(TEXT_COLUMN_FEATURE, "text_column")
    assert "name: str" in signature


@pytest.mark.pending
def test_no_examples_table_infers_str_parameter() -> None:
    signature = emitted_function_signature(NO_EXAMPLES_FEATURE, "no_examples")
    assert "name: str" in signature
