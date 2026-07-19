from __future__ import annotations

from typing import TYPE_CHECKING

from beehave.gherkin import Rule, parse_feature

if TYPE_CHECKING:
    from beehave.gherkin import Scenario, Step


def _placeholder_names(steps: list[Step]) -> list[str]:
    seen: set[str] = set()
    names: list[str] = []
    for step in steps:
        for placeholder in step.placeholders:
            if placeholder.name not in seen:
                seen.add(placeholder.name)
                names.append(placeholder.name)
    return names


def _signature_line(scenario: Scenario) -> str:
    names = _placeholder_names(scenario.steps)
    params = ", ".join(f"{name}: str" for name in names)
    return f"def {scenario.function_name}({params}) -> None: ..."


def check(feature_text: str, stub_text: str) -> bool:
    feature = parse_feature(feature_text)
    for child in feature.children:
        scenarios = child.children if isinstance(child, Rule) else [child]
        for scenario in scenarios:
            if _signature_line(scenario) not in stub_text:
                return False
    return True
