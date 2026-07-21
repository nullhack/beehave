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


def test_check_fails_when_py_missing_scenario_fn(pytester) -> None:
    initial = "Feature: Stale Check\nScenario: first scenario\nGiven a step\n"
    write_feature_text(pytester, "stale.feature", initial)
    pytester.run("beehave", "generate")
    updated = initial + "Scenario: second scenario\nGiven another step\n"
    write_feature_text(pytester, "stale.feature", updated)
    assert run_beehave_check(pytester) != 0


def test_check_fails_on_orphan_module_in_tests_features(pytester) -> None:
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


def test_check_fails_when_py_fn_signature_drifts(pytester) -> None:
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


def test_check_passes_with_private_helpers_in_py(pytester) -> None:
    feature_text = "Feature: Private Helper\nScenario: main scenario\nGiven anything\n"
    write_feature_text(pytester, "private.feature", feature_text)
    pytester.run("beehave", "generate")
    py_path = pytester.path / "tests" / "features" / "private_default_test.py"
    py_text = py_path.read_text()
    helper = "\n\ndef _helper():\n    return 42\n"
    py_path.write_text(py_text + helper)
    assert run_beehave_check(pytester) == 0


def test_check_fails_when_py_has_extra_non_private_fn(pytester) -> None:
    feature_text = "Feature: Extra Fn\nScenario: main scenario\nGiven anything\n"
    write_feature_text(pytester, "extra.feature", feature_text)
    pytester.run("beehave", "generate")
    py_path = pytester.path / "tests" / "features" / "extra_default_test.py"
    py_text = py_path.read_text()
    extra_fn = "\n\ndef test_extra_orphan():\n    pass\n"
    py_path.write_text(py_text + extra_fn)
    assert run_beehave_check(pytester) != 0


def test_check_scoped_to_one_feature_path(pytester) -> None:
    copy_feature_into_pytester(pytester, HIVE_ACTIVITY_FEATURE)
    write_feature_text(
        pytester,
        "other.feature",
        "Feature: Other\nScenario: other scenario\nGiven anything\n",
    )
    pytester.run("beehave", "generate")
    assert run_beehave_check(pytester, "docs/features/hive_activity.feature") == 0


def test_check_scoped_skips_orphan_module_detection(pytester) -> None:
    copy_feature_into_pytester(pytester, HIVE_ACTIVITY_FEATURE)
    pytester.run("beehave", "generate")
    orphan_path = pytester.path / "tests" / "features" / "orphan_default_test.py"
    orphan_path.write_text("# orphan")
    result = pytester.run("beehave", "check", "docs/features/hive_activity.feature")
    assert result.ret == 0
    assert "orphan" not in "\n".join(result.errlines)


def test_check_scoped_fails_on_drift_in_targeted_feature(pytester) -> None:
    copy_feature_into_pytester(pytester, HIVE_ACTIVITY_FEATURE)
    pytester.run("beehave", "generate")
    py_path = pytester.path / "tests" / "features" / "hive_activity_default_test.py"
    py_text = py_path.read_text()
    edited = py_text.replace(
        "def test_honey_production_from_nectar(nectar: str",
        "def test_honey_production_from_nectar(renamed: str",
        1,
    )
    assert edited != py_text
    py_path.write_text(edited)
    assert run_beehave_check(pytester, "docs/features/hive_activity.feature") != 0


def test_check_scoped_fails_on_nonexistent_path(pytester) -> None:
    copy_feature_into_pytester(pytester, HIVE_ACTIVITY_FEATURE)
    pytester.run("beehave", "generate")
    result = pytester.run("beehave", "check", "docs/features/missing.feature")
    assert result.ret != 0
    assert "not a feature file" in "\n".join(result.errlines)


def test_check_scoped_fails_on_non_feature_file(pytester) -> None:
    copy_feature_into_pytester(pytester, HIVE_ACTIVITY_FEATURE)
    pytester.run("beehave", "generate")
    readme = pytester.path / "README.md"
    readme.write_text("# not a feature")
    result = pytester.run("beehave", "check", "README.md")
    assert result.ret != 0
