"""Step context manager for Gherkin steps."""

from collections.abc import Iterator
from contextlib import contextmanager


@contextmanager
def step(
    keyword: str,
    text: str,
    /,
    **placeholders: object,
) -> Iterator[None]:
    """Attach the step's keyword and text as a note to any exception raised inside."""
    try:
        yield
    except Exception as e:
        e.add_note(f"{keyword} {text}")
        raise
