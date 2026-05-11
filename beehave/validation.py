from dataclasses import dataclass


@dataclass(frozen=True)
class Mismatch:
    expected: str
    actual: str


def validate_step_text(feature_step: str, decorator_step: str) -> Mismatch | None:
    raise NotImplementedError
