import re
from dataclasses import dataclass, field
from enum import IntEnum


@dataclass(frozen=True)
class Mismatch:
    """A difference between decorator step text and .feature step text.

    Attributes:
        expected: The step text from the .feature file.
        actual: The step text from the test decorator.
    """

    expected: str
    actual: str


@dataclass(frozen=True)
class OrderingViolation:
    """An ordering violation where a step appears out of Given→When→Then sequence.

    Attributes:
        step_index: The zero-based index of the violating step.
        actual_keyword: The effective keyword of the step (after @And/@But resolution).
        expected_after: The keyword(s) that should have preceded this step type.
    """

    step_index: int
    actual_keyword: str
    expected_after: str


class AdoptionLevel(IntEnum):
    """Progressive opt-in level determining which validations are active.

    Attributes:
        DECORATORS_ONLY: Level 1 — validates ordering and placeholders.
        FEATURE_TRACEABILITY: Level 2 — adds step text, @id, and orphan checks.
    """

    DECORATORS_ONLY = 1
    FEATURE_TRACEABILITY = 2


@dataclass
class ValidationReport:
    """A report of mismatches, ordering violations, and orphan detections.

    Attributes:
        mismatches: Step text mismatches between decorator and .feature.
        ordering_violations: Steps that violate Given→When→Then ordering.
        orphan_tests: Test functions with no matching .feature scenario.
        orphan_scenarios: .feature scenarios with no matching test function.
    """

    mismatches: list[Mismatch] = field(default_factory=list)
    ordering_violations: list[OrderingViolation] = field(default_factory=list)
    orphan_tests: list[str] = field(default_factory=list)
    orphan_scenarios: list[str] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return (
            not self.mismatches
            and not self.ordering_violations
            and not self.orphan_tests
            and not self.orphan_scenarios
        )


def validate_step_text(feature_step: str, decorator_step: str) -> Mismatch | None:
    """Validate that decorator step text matches feature step text exactly.

    Args:
        feature_step: The step text from the .feature file.
        decorator_step: The step text from the test decorator.

    Returns:
        None if the texts match, or a Mismatch carrying both texts.
    """
    if feature_step == decorator_step:
        return None
    return Mismatch(expected=feature_step, actual=decorator_step)


_KEYWORD_RANK = {"Given": 0, "When": 1, "Then": 2}

_RANK_LABEL = {0: "Given", 1: "When", 2: "Then"}


def _expected_after_description(keyword: str) -> str:
    """Return a human-readable description of what should precede this keyword."""
    rank = _KEYWORD_RANK[keyword]
    preceding = [_RANK_LABEL[r] for r in sorted(_RANK_LABEL) if r < rank]
    if preceding:
        if len(preceding) == 1:
            return f"{keyword} must come after {preceding[0]}"
        return f"{keyword} must come after {'/'.join(preceding)}"
    return f"{keyword} must come first"


_INHERITING_KEYWORDS = {"And", "But"}


def validate_step_ordering(
    steps: list[tuple[str, str]],
) -> list[OrderingViolation]:
    """Validate that steps follow Given → When → Then ordering.

    @And/@But keywords inherit their effective type from the preceding
    Given/When/Then keyword. A step appearing before any defining keyword
    (e.g. And as the first step) is reported as a violation.

    Args:
        steps: Ordered list of (keyword, text) tuples from the test function.

    Returns:
        A list of OrderingViolation for each step that breaks the ordering
        rule. An empty list means all steps are correctly ordered.
    """
    violations: list[OrderingViolation] = []
    prev_rank = -1
    last_defining_keyword: str | None = None
    for i, (keyword, _text) in enumerate(steps):
        if keyword in _INHERITING_KEYWORDS:
            effective_keyword = last_defining_keyword
        else:
            effective_keyword = keyword
            last_defining_keyword = keyword
        if effective_keyword is None:
            violations.append(
                OrderingViolation(
                    step_index=i,
                    actual_keyword=keyword,
                    expected_after="Given/When/Then must precede And/But",
                )
            )
            continue
        rank = _KEYWORD_RANK[effective_keyword]
        if rank < prev_rank:
            violations.append(
                OrderingViolation(
                    step_index=i,
                    actual_keyword=effective_keyword,
                    expected_after=_expected_after_description(effective_keyword),
                )
            )
        prev_rank = rank
    return violations


def validate_placeholders(
    step_text: str,
    param_names: list[str],
) -> list[Mismatch]:
    """Validate that all <placeholder> tokens in step_text exist in param_names.

    Args:
        step_text: The step text containing <placeholder> tokens.
        param_names: The parameter names from the function signature.

    Returns:
        An empty list if all placeholders match, or a list of Mismatch objects
        for any placeholders not found in param_names.
    """
    placeholders = re.findall(r"<(\w+)>", step_text)
    param_set = set(param_names)
    mismatches: list[Mismatch] = []
    for name in placeholders:
        if name not in param_set:
            mismatches.append(
                Mismatch(
                    expected=f"<{name}> not found in function parameters",
                    actual=step_text,
                )
            )
    return mismatches
