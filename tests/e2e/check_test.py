from __future__ import annotations

import shutil
from pathlib import Path

HIVE_ACTIVITY_FEATURE = "hive_activity.feature"


def copy_feature_into_pytester(pytester, basename: str) -> str:
    src = Path(__file__).resolve().parents[2] / "docs" / "features" / basename
    dst = pytester.path / "docs" / "features" / basename
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(src, dst)
    return str(dst)


def write_feature_text(pytester, basename: str, text: str) -> str:
    dst = pytester.path / "docs" / "features" / basename
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text)
    return str(dst)


def run_beehave_check(pytester, *args: str) -> int:
    return pytester.run("beehave", "check", *args).ret


def test_check_passes_on_freshly_generated_project(pytester) -> None:
    copy_feature_into_pytester(pytester, HIVE_ACTIVITY_FEATURE)
    pytester.run("beehave", "generate")
    assert run_beehave_check(pytester) == 0


def test_check_fails_when_pyi_stale_after_feature_adds_scenario(pytester) -> None:
    initial = "Feature: Stale Check\nScenario: first scenario\nGiven a step\n"
    write_feature_text(pytester, "stale.feature", initial)
    pytester.run("beehave", "generate")
    updated = initial + "Scenario: second scenario\nGiven another step\n"
    write_feature_text(pytester, "stale.feature", updated)
    assert run_beehave_check(pytester) != 0


def test_check_fails_on_orphan_py_in_tests_features(pytester) -> None:
    copy_feature_into_pytester(pytester, HIVE_ACTIVITY_FEATURE)
    pytester.run("beehave", "generate")
    orphan_path = pytester.path / "tests" / "features" / "orphan_default_test.py"
    orphan_path.write_text("# orphan")
    result = pytester.run("beehave", "check")
    assert result.ret != 0
    assert "orphan" in "\n".join(result.errlines)


def test_check_ignores_handwritten_py_outside_tests_features(pytester) -> None:
    copy_feature_into_pytester(pytester, HIVE_ACTIVITY_FEATURE)
    pytester.run("beehave", "generate")
    handwritten = pytester.path / "tests" / "handwritten_test.py"
    handwritten.parent.mkdir(parents=True, exist_ok=True)
    handwritten.write_text("# handwritten")
    assert run_beehave_check(pytester) == 0


def test_check_fails_when_py_drifts_from_pyi(pytester) -> None:
    outline = (
        "Feature: Drift Check\n"
        "Scenario Outline: drift scenario\n"
        "Given a value of <amount>\n"
        "\n"
        "Examples:\n"
        "  | amount |\n"
        "  | 1      |\n"
    )
    write_feature_text(pytester, "drift.feature", outline)
    pytester.run("beehave", "generate")
    py_path = pytester.path / "tests" / "features" / "drift_default_test.py"
    py_text = py_path.read_text()
    edited = py_text.replace(
        "def test_drift_scenario(amount: str)",
        "def test_drift_scenario(renamed: str)",
    )
    assert edited != py_text
    py_path.write_text(edited)
    assert run_beehave_check(pytester) != 0
