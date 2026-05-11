from dataclasses import dataclass


@dataclass(frozen=True)
class Mismatch:
    """A difference between decorator step text and .feature step text.

    Attributes:
        expected: The step text from the .feature file.
        actual: The step text from the test decorator.
    """

    expected: str
    actual: str


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
