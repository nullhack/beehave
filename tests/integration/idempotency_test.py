from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

BASE_FEATURE = """\
Feature: Input
Scenario: first scenario
Given anything
"""

EXTENDED_FEATURE = """\
Feature: Input
Scenario: first scenario
Given anything

Scenario: second scenario
Given anything
"""


def emit_test_py_for(feature_text: str) -> str:
    from beehave.generate import generate

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        features = root / "docs" / "features"
        features.mkdir(parents=True)
        (features / "input.feature").write_text(feature_text)
        generate(root)
        return (root / "tests" / "input_default_test.py").read_text()


def emit_test_pyi_for(feature_text: str) -> str:
    from beehave.generate import generate

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        features = root / "docs" / "features"
        features.mkdir(parents=True)
        (features / "input.feature").write_text(feature_text)
        generate(root)
        return (root / "tests" / "input_default_test.pyi").read_text()


def regenerate_over_body(feature_text: str, existing_py_body: str) -> str:
    from beehave.generate import generate

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        features = root / "docs" / "features"
        features.mkdir(parents=True)
        (features / "input.feature").write_text(feature_text)
        tests_dir = root / "tests"
        tests_dir.mkdir(parents=True)
        py_path = tests_dir / "input_default_test.py"
        py_path.write_text(existing_py_body)
        generate(root)
        return py_path.read_text()


@pytest.mark.pending
def test_regenerate_preserves_existing_consumer_py_body() -> None:
    consumer_marker = "# consumer-authored marker line"
    regenerated = regenerate_over_body(BASE_FEATURE, consumer_marker)
    assert consumer_marker in regenerated


@pytest.mark.pending
def test_regenerate_does_not_emit_py_when_py_present() -> None:
    consumer_body = (
        "from beehave import step\n"
        "\n"
        "def test_first_scenario():\n"
        '    with step("Given", "anything"):\n'
        "        pass\n"
    )
    regenerated = regenerate_over_body(BASE_FEATURE, consumer_body)
    assert regenerated == consumer_body


@pytest.mark.pending
def test_regenerate_rewrites_pyi_when_feature_gains_scenario() -> None:
    pyi = emit_test_pyi_for(EXTENDED_FEATURE)
    assert "test_second_scenario" in pyi
