from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum


class StepStatus(IntEnum):
    """Status of a step in a failure report.

    Attributes:
        PASSED: Step executed successfully.
        FAILED: Step raised an exception.
        NOT_REACHED: Step was not executed due to prior failure.
    """

    PASSED = 1
    FAILED = 2
    NOT_REACHED = 3


@dataclass(frozen=True)
class StepReport:
    """A rendered step with status and optional exception message.

    Attributes:
        step_keyword: The Gherkin keyword (Given/When/Then/And/But).
        step_text: The rendered step text with placeholders substituted.
        status: The execution status of this step.
        exception_message: The exception message if the step failed.
    """

    step_keyword: str
    step_text: str
    status: StepStatus
    exception_message: str | None = None


@dataclass
class FailureReport:
    """A composed failure report with step statuses and heuristic metadata.

    Attributes:
        steps: Ordered list of step reports.
        is_assertion_error: Whether the exception was an AssertionError.
        failed_step_index: Index of the failed step.
    """

    steps: list[StepReport] = field(default_factory=list)
    is_assertion_error: bool = False
    failed_step_index: int | None = None


def render_failure_report(
    steps: list[tuple[str, str]],
    exception: BaseException | None,
    counterexample: dict[str, object],
    *,
    failed_step_index: int | None = None,
) -> FailureReport | None:
    """Render a failure report from step metadata and an exception.

    Uses the Then-failed heuristic for AssertionErrors (defaults to last
    step). Non-assertion exceptions require an explicit ``failed_step_index``
    via the line-number heuristic resolved by the caller.

    Args:
        steps: List of (keyword, template) tuples for each step.
        exception: The exception that caused the test failure, or None.
        counterexample: Parameter values for placeholder substitution.
        failed_step_index: Explicit index of the failed step.

    Returns:
        A FailureReport, or None if exception is None.
    """
    if exception is None:
        return None

    is_assertion = isinstance(exception, AssertionError)
    # Use explicit index if provided;
    # otherwise attribute AssertionError to the last step
    if failed_step_index is not None:
        failed_index = failed_step_index
    elif is_assertion:
        failed_index = len(steps) - 1
    else:
        failed_index = len(steps) - 1

    step_reports: list[StepReport] = []
    for i, (keyword, template) in enumerate(steps):
        text = render_step_text(template, counterexample)
        if i < failed_index:
            step_reports.append(StepReport(keyword, text, StepStatus.PASSED))
        elif i == failed_index:
            step_reports.append(
                StepReport(keyword, text, StepStatus.FAILED, str(exception))
            )
        else:
            step_reports.append(StepReport(keyword, text, StepStatus.NOT_REACHED))

    return FailureReport(
        steps=step_reports,
        is_assertion_error=is_assertion,
        failed_step_index=failed_index,
    )


def render_step_text(template: str, values: dict[str, object]) -> str:
    """Replace <placeholder> tokens in template with string values.

    Args:
        template: Step text with ``<key>`` placeholder tokens.
        values: Mapping of placeholder names to substitution values.

    Returns:
        The template with all matched placeholders replaced.
    """
    result = template
    for key, value in values.items():
        result = result.replace(f"<{key}>", str(value))
    return result
