from __future__ import annotations

import sys
from collections.abc import Iterator
from contextlib import contextmanager
from types import FrameType
from typing import TYPE_CHECKING

from beehave._index import NoActiveScenarioError, get

if TYPE_CHECKING:
    from beehave.gherkin import Scenario


class StepError(Exception):
    """Raised when a step() block fails runtime verification."""


_counters: dict[int, int] = {}


def _row_values(row: object) -> tuple[object, ...]:
    if hasattr(row, "values"):
        return tuple(row.values)  # type: ignore[attr-defined]
    return tuple(row)  # type: ignore[arg-type]


def _verify_parametrize(frame: FrameType, func_name: str, scenario: Scenario) -> None:
    examples = scenario.examples
    if examples is None:
        return
    func = frame.f_globals.get(func_name)
    if func is None:
        return
    marks = getattr(func, "pytestmark", [])
    expected_names = tuple(examples.headers)
    expected_rows = [tuple(row[h] for h in examples.headers) for row in examples.rows]
    for mark in marks:
        if getattr(mark, "name", None) != "parametrize":
            continue
        args = mark.args
        if len(args) < 2:
            raise StepError(f"{func_name}: @parametrize has too few args")
        actual_names = tuple(args[0])
        actual_rows = [_row_values(r) for r in args[1]]
        if actual_names != expected_names or actual_rows != expected_rows:
            raise StepError(
                f"{func_name}: @parametrize does not match Examples "
                f"(expected names={expected_names}, rows={expected_rows}; "
                f"got names={actual_names}, rows={actual_rows})"
            )
        return
    raise StepError(
        f"{func_name}: scenario has Examples but function lacks @parametrize"
    )


@contextmanager
def step(
    keyword: str,
    text: str,
    /,
    **placeholders: object,
) -> Iterator[None]:
    frame = sys._getframe(1)
    while frame is not None and not frame.f_code.co_name.startswith("test_"):
        frame = frame.f_back
    if frame is None:
        raise NoActiveScenarioError(
            "step() must be called from a test_<slug> function body"
        )
    func_name = frame.f_code.co_name
    scenario = get(func_name)
    position = _counters.get(id(frame), 0)
    if position >= len(scenario.steps):
        raise StepError(
            f"{func_name}: too many step() calls (expected {len(scenario.steps)})"
        )
    expected = scenario.steps[position]
    next_position = position + 1
    if next_position >= len(scenario.steps):
        _counters.pop(id(frame), None)
    else:
        _counters[id(frame)] = next_position
    expected_names = {p.name for p in expected.placeholders}
    actual_names = set(placeholders.keys())
    if (
        keyword.lower() != expected.keyword.lower()
        or text != expected.text
        or actual_names != expected_names
    ):
        raise StepError(
            f"{func_name}: step {position} mismatch "
            f"(expected keyword={expected.keyword!r}, text={expected.text!r}, "
            f"placeholders={expected_names}; "
            f"got keyword={keyword!r}, text={text!r}, placeholders={actual_names})"
        )
    if position == 0:
        _verify_parametrize(frame, func_name, scenario)
    try:
        yield
    except Exception as e:
        e.add_note(f"{keyword} {text}")
        raise
