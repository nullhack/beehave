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
        return (root / "tests" / "features" / "input_default_test.py").read_text()


def check_passes_for(feature_text: str, py_text: str) -> bool:
    from beehave.check import check

    return check(feature_text, py_text)


def test_check_passes_on_freshly_generated_py() -> None:
    py_text = emit_test_py_for(ROUND_TRIP_FEATURE)
    assert check_passes_for(ROUND_TRIP_FEATURE, py_text)


def test_check_fails_when_py_missing_signature() -> None:
    assert not check_passes_for(ROUND_TRIP_FEATURE, "")


def test_check_fails_when_py_signature_renamed() -> None:
    py_text = emit_test_py_for(ROUND_TRIP_FEATURE)
    edited = py_text.replace("test_round_trip", "test_renamed")
    assert edited != py_text
    assert not check_passes_for(ROUND_TRIP_FEATURE, edited)
