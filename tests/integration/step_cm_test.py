from __future__ import annotations

import pytest

NOTE_FORMAT = "{keyword} {text}"


def test_block_body_executes_when_entered() -> None:
    from beehave import step

    side_effect: list[str] = []
    with step("Given", "the hive is active"):
        side_effect.append("entered")
    assert side_effect == ["entered"]


def test_assertion_inside_then_step_propagates_failure() -> None:
    from beehave import step

    with pytest.raises(AssertionError), step("Then", "the hive has honey"):
        raise AssertionError


def test_assertion_inside_then_step_passes_when_truthy() -> None:
    from beehave import step

    with step("Then", "the hive has honey"):
        assert True


def test_exception_attributed_to_step_via_add_note() -> None:
    from beehave import step

    keyword = "Then"
    text = "the hive has honey"
    with pytest.raises(AssertionError) as exc_info, step(keyword, text):
        raise AssertionError
    assert exc_info.value.__notes__ == [
        NOTE_FORMAT.format(keyword=keyword, text=text),
    ]


def test_clean_exit_does_not_add_attribution_note() -> None:
    from beehave import step

    with step("Given", "the hive is active"):
        pass


def test_keyword_and_text_are_positional_only() -> None:
    from beehave import step

    with pytest.raises(TypeError):
        step(keyword="Then", text="the hive has honey")  # type: ignore[call-arg]


def test_placeholders_accepted_as_keyword_arguments() -> None:
    from beehave import step

    with step("Given", "the hive has <nectar> grams", nectar=100):
        pass


def test_all_gherkin_step_keywords_accepted() -> None:
    from beehave import step

    keywords = ["Given", "When", "Then", "And", "But", "*"]
    for keyword in keywords:
        with step(keyword, "any step text"):
            pass


def test_localized_keyword_accepted() -> None:
    from beehave import step

    with step("Допустим", "улей активен"):
        pass
