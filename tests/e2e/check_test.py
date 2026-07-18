from __future__ import annotations

import shutil
from pathlib import Path

HIVE_ACTIVITY_FEATURE = "hive_activity.feature"
COMB_CONSTRUCTION_FEATURE = "comb_construction.feature"


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


def write_test_py(pytester, stem: str, body: str) -> str:
    dst = pytester.path / "tests" / f"{stem}_test.py"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(body)
    return str(dst)


def run_beehave_check(pytester, *args: str) -> int:
    return pytester.run("beehave", "check", *args).ret


def test_passes_when_blocks_match_steps(pytester) -> None:
    copy_feature_into_pytester(pytester, HIVE_ACTIVITY_FEATURE)
    pytester.run("beehave", "generate")
    assert run_beehave_check(pytester) == 0


def test_fails_when_block_count_differs_from_step_count(pytester) -> None:
    feature_text = (
        "Feature: Minimal\n"
        "Scenario: minimal scenario\n"
        "Given first step\n"
        "When second step\n"
    )
    write_feature_text(pytester, "minimal.feature", feature_text)
    short_body = (
        "from beehave import step\n"
        "\n"
        "def test_minimal_scenario():\n"
        '    with step("Given", "first step"):\n'
        "        pass\n"
    )
    write_test_py(pytester, "minimal_default", short_body)
    assert run_beehave_check(pytester) != 0


def test_fails_when_step_keyword_structurally_mismatches(pytester) -> None:
    feature_text = (
        "Feature: Minimal\n"
        "Scenario: minimal scenario\n"
        "Given first step\n"
        "When second step\n"
    )
    write_feature_text(pytester, "minimal.feature", feature_text)
    mismatched_body = (
        "from beehave import step\n"
        "\n"
        "def test_minimal_scenario():\n"
        '    with step("Given", "first step"):\n'
        "        pass\n"
        '    with step("Given", "second step"):\n'
        "        pass\n"
    )
    write_test_py(pytester, "minimal_default", mismatched_body)
    assert run_beehave_check(pytester) != 0


def test_fails_when_step_text_mismatches(pytester) -> None:
    feature_text = (
        "Feature: Minimal\n"
        "Scenario: minimal scenario\n"
        "Given first step\n"
        "When second step\n"
    )
    write_feature_text(pytester, "minimal.feature", feature_text)
    mismatched_body = (
        "from beehave import step\n"
        "\n"
        "def test_minimal_scenario():\n"
        '    with step("Given", "first step"):\n'
        "        pass\n"
        '    with step("When", "different text"):\n'
        "        pass\n"
    )
    write_test_py(pytester, "minimal_default", mismatched_body)
    assert run_beehave_check(pytester) != 0


def test_fails_when_placeholder_name_set_mismatches(pytester) -> None:
    feature_text = (
        "Feature: Minimal\n"
        "Scenario Outline: minimal scenario\n"
        "Given a value of <amount>\n"
        "When anything\n"
        "\n"
        "Examples:\n"
        "  | amount |\n"
        "  | 1      |\n"
    )
    write_feature_text(pytester, "minimal.feature", feature_text)
    mismatched_body = (
        "from beehave import step\n"
        "\n"
        "def test_minimal_scenario(amount):\n"
        '    with step("Given", "a value of <amount>", renamed=1):\n'
        "        pass\n"
        '    with step("When", "anything"):\n'
        "        pass\n"
    )
    write_test_py(pytester, "minimal_default", mismatched_body)
    assert run_beehave_check(pytester) != 0


def test_passes_when_keyword_case_differs(pytester) -> None:
    feature_text = (
        "Feature: Minimal\n"
        "Scenario: minimal scenario\n"
        "Given first step\n"
        "When second step\n"
    )
    write_feature_text(pytester, "minimal.feature", feature_text)
    case_body = (
        "from beehave import step\n"
        "\n"
        "def test_minimal_scenario():\n"
        '    with step("given", "first step"):\n'
        "        pass\n"
        '    with step("when", "second step"):\n'
        "        pass\n"
    )
    write_test_py(pytester, "minimal_default", case_body)
    assert run_beehave_check(pytester) == 0


def test_passes_with_arbitrary_body_content_inside_step_block(pytester) -> None:
    feature_text = (
        "Feature: Minimal\n"
        "Scenario: minimal scenario\n"
        "Given first step\n"
        "When second step\n"
    )
    write_feature_text(pytester, "minimal.feature", feature_text)
    body_with_content = (
        "from beehave import step\n"
        "\n"
        "def test_minimal_scenario():\n"
        '    with step("Given", "first step"):\n'
        "        x = 1 + 1\n"
        "        y = x * 2\n"
        '    with step("When", "second step"):\n'
        "        z = y + 1\n"
    )
    write_test_py(pytester, "minimal_default", body_with_content)
    assert run_beehave_check(pytester) == 0


def test_does_not_inspect_body_for_literals_or_placeholders(pytester) -> None:
    feature_text = (
        "Feature: Minimal\n"
        "Scenario: minimal scenario\n"
        "Given first step\n"
        "When second step\n"
    )
    write_feature_text(pytester, "minimal.feature", feature_text)
    body_without_literals = (
        "from beehave import step\n"
        "\n"
        "def test_minimal_scenario():\n"
        '    with step("Given", "first step"):\n'
        "        pass\n"
        '    with step("When", "second step"):\n'
        "        pass\n"
    )
    write_test_py(pytester, "minimal_default", body_without_literals)
    assert run_beehave_check(pytester) == 0
