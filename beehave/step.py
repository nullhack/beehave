from collections.abc import Iterator
from contextlib import contextmanager


@contextmanager
def step(
    keyword: str,
    text: str,
    /,
    **placeholders: object,
) -> Iterator[None]:
    try:
        yield
    except Exception as e:
        e.add_note(f"{keyword} {text}")
        raise
