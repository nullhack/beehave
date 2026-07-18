from __future__ import annotations

from typing import cast

MIN_WORD_COUNT = 2
MAX_WORD_COUNT = 6


def function_name_for_title(title: str) -> str:
    from beehave.gherkin import Scenario, parse_feature

    feature_text = f"Feature: T\nScenario: {title}\nGiven any step\n"
    feature = parse_feature(feature_text)
    return cast(Scenario, feature.children[0]).function_name


def title_is_valid_in_feature(*titles: str) -> bool:
    from beehave.gherkin import parse_feature

    scenarios = "\n".join(f"Scenario: {t}\nGiven any step\n" for t in titles)
    feature_text = f"Feature: T\n{scenarios}"
    try:
        parse_feature(feature_text)
    except Exception:
        return False
    return True


def test_title_lowered_to_slug() -> None:
    assert function_name_for_title("Honey Production") == "test_honey_production"


def test_whitespace_runs_collapse_to_single_underscore() -> None:
    assert function_name_for_title("Honey   Production") == "test_honey_production"


def test_function_name_is_test_underscore_slug() -> None:
    assert (
        function_name_for_title("forager returns with nectar")
        == "test_forager_returns_with_nectar"
    )


def test_two_word_title_is_valid() -> None:
    assert title_is_valid_in_feature("Honey Production")


def test_six_word_title_is_valid() -> None:
    assert title_is_valid_in_feature("the forager returns to the hive")


def test_one_word_title_rejected() -> None:
    assert not title_is_valid_in_feature("Honey")


def test_seven_word_title_rejected() -> None:
    assert not title_is_valid_in_feature("the forager returns to the busy hive")


def test_title_with_hyphen_rejected() -> None:
    assert not title_is_valid_in_feature("Honey-Production")


def test_duplicate_titles_case_insensitive_rejected() -> None:
    assert not title_is_valid_in_feature("Hive Activity", "hive activity")
