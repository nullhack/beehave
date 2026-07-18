from __future__ import annotations

import tempfile
from pathlib import Path

ROUND_TRIP_FEATURE = """\
Feature: Roundtrip Contract
Scenario: round trip
Given first step
When second step
Then third step
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


def check_passes_for(feature_text: str, test_py_text: str) -> bool:
    from beehave.check import check

    return check(feature_text, test_py_text)


def test_check_passes_on_freshly_generated_py() -> None:
    py_text = emit_test_py_for(ROUND_TRIP_FEATURE)
    assert check_passes_for(ROUND_TRIP_FEATURE, py_text)


def test_check_fails_after_consumer_edits_step_text() -> None:
    py_text = emit_test_py_for(ROUND_TRIP_FEATURE)
    edited = py_text.replace("first step", "edited step text")
    assert not check_passes_for(ROUND_TRIP_FEATURE, edited)


def test_check_fails_after_consumer_removes_step_block() -> None:
    shorter_body = (
        "from beehave import step\n"
        "\n"
        "def test_round_trip():\n"
        '    with step("Given", "first step"):\n'
        "        pass\n"
    )
    assert not check_passes_for(ROUND_TRIP_FEATURE, shorter_body)


def test_check_passes_after_consumer_adds_body_content() -> None:
    body_with_extra = (
        "from beehave import step\n"
        "\n"
        "def test_round_trip():\n"
        '    with step("Given", "first step"):\n'
        "        x = 1 + 1\n"
        '    with step("When", "second step"):\n'
        "        pass\n"
        '    with step("Then", "third step"):\n'
        "        pass\n"
    )
    assert check_passes_for(ROUND_TRIP_FEATURE, body_with_extra)
