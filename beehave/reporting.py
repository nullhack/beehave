from dataclasses import dataclass, field
from enum import IntEnum


class StepStatus(IntEnum):
    PASSED = 1
    FAILED = 2
    NOT_REACHED = 3


@dataclass(frozen=True)
class StepReport:
    step_keyword: str
    step_text: str
    status: StepStatus
    exception_message: str | None = None


@dataclass
class FailureReport:
    steps: list[StepReport] = field(default_factory=list)
    is_assertion_error: bool = False
    failed_step_index: int | None = None


def render_failure_report(steps, exception, counterexample):
    raise NotImplementedError


def render_step_text(template, values):
    raise NotImplementedError
