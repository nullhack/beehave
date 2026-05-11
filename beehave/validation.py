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
        raise NotImplementedError


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


def validate_step_ordering(
    steps: list[tuple[str, str]],
) -> list[OrderingViolation]:
    raise NotImplementedError


def validate_placeholders(
    step_text: str, param_names: list[str],
) -> list[Mismatch]:
    raise NotImplementedError
