from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from beehave.gherkin import Scenario


class NoActiveScenarioError(Exception):
    """Raised when a step() call's calling function is not a known scenario."""


_index: dict[str, Scenario] | None = None


def _build_index() -> dict[str, Scenario]:
    from beehave.gherkin import Rule, parse_feature

    features_dir = Path.cwd() / "docs" / "features"
    index: dict[str, Scenario] = {}
    if not features_dir.is_dir():
        return index
    for feature_path in sorted(features_dir.glob("*.feature")):
        feature = parse_feature(feature_path.read_text())
        for child in feature.children:
            scenarios = child.children if isinstance(child, Rule) else [child]
            for scenario in scenarios:
                index[scenario.function_name] = scenario
    return index


def get(function_name: str) -> Scenario:
    global _index
    if _index is None:
        _index = _build_index()
    if function_name not in _index:
        raise NoActiveScenarioError(
            f"{function_name!r} is not a known scenario function; "
            f"step() may only be called inside a generated test body"
        )
    return _index[function_name]


def _reset() -> None:
    """Drop the cached index (test hook; not for consumer use)."""
    global _index
    _index = None
