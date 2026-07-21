from __future__ import annotations

import pytest

STEP_RUNTIME_FEATURE = """\
Feature: Step Runtime

Scenario: block executes
    Given the hive is active

Scenario: attribution note added
    Then the hive has honey

Scenario: wrong keyword fails
    Given the hive is active

Scenario: wrong text fails
    Given the hive is active

Scenario: wrong placeholders fail
    Given the hive has <nectar> grams

Scenario: too many steps fail
    Given the only step

Scenario Outline: parametrize verifies ok
    Given nectar of <amount>
    When hours of <duration>
    Then honey of <honey>

    Examples:
      | amount | duration | honey |
      | 100    | 8        | 80    |
      | 200    | 12       | 150   |

Scenario Outline: parametrize mismatch fails
    Given nectar of <amount>

    Examples:
      | amount |
      | 100    |
"""


@pytest.fixture
def step_project(tmp_path: str, monkeypatch: pytest.MonkeyPatch) -> None:
    from pathlib import Path

    from beehave import _index

    features = Path(tmp_path) / "docs" / "features"
    features.mkdir(parents=True)
    (features / "step_runtime.feature").write_text(STEP_RUNTIME_FEATURE)
    monkeypatch.chdir(Path(tmp_path))
    _index._reset()
    yield
    _index._reset()


def test_block_executes(step_project: None) -> None:
    from beehave import step

    side_effect: list[str] = []
    with step("Given", "the hive is active"):
        side_effect.append("entered")
    assert side_effect == ["entered"]


def test_attribution_note_added(step_project: None) -> None:
    from beehave import step

    keyword = "Then"
    text = "the hive has honey"
    with pytest.raises(AssertionError) as exc_info, step(keyword, text):
        raise AssertionError
    assert exc_info.value.__notes__ == [f"{keyword} {text}"]


def test_wrong_keyword_fails(step_project: None) -> None:
    from beehave import StepError, step

    with pytest.raises(StepError), step("When", "the hive is active"):
        pass


def test_wrong_text_fails(step_project: None) -> None:
    from beehave import StepError, step

    with pytest.raises(StepError), step("Given", "different text"):
        pass


def test_wrong_placeholders_fail(step_project: None) -> None:
    from beehave import StepError, step

    with (
        pytest.raises(StepError),
        step("Given", "the hive has <nectar> grams", wrong=1),
    ):
        pass


def test_too_many_steps_fail(step_project: None) -> None:
    from beehave import StepError, step

    with step("Given", "the only step"):
        pass
    with pytest.raises(StepError), step("When", "second step"):
        pass


def test_unknown_function_raises_no_active_scenario(
    step_project: None,
) -> None:
    from beehave import NoActiveScenarioError, step

    with pytest.raises(NoActiveScenarioError), step("Given", "anything"):
        pass


@pytest.mark.parametrize(
    ("amount", "duration", "honey"),
    [("100", "8", "80"), ("200", "12", "150")],
)
def test_parametrize_verifies_ok(
    step_project: None,
    amount: str,
    duration: str,
    honey: str,
) -> None:
    from beehave import step

    with step("Given", "nectar of <amount>", amount=amount):
        pass
    with step("When", "hours of <duration>", duration=duration):
        pass
    with step("Then", "honey of <honey>", honey=honey):
        pass


@pytest.mark.parametrize(("amount",), [("999",)])
def test_parametrize_mismatch_fails(
    step_project: None,
    amount: str,
) -> None:
    from beehave import StepError, step

    with pytest.raises(StepError), step("Given", "nectar of <amount>", amount=amount):
        pass


def test_keyword_and_text_are_positional_only() -> None:
    from beehave import step

    with pytest.raises(TypeError):
        step(keyword="Then", text="the hive has honey")  # type: ignore[call-arg]
