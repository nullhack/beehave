from collections.abc import Iterator
from contextlib import contextmanager

# v2.3 Mode B runtime enforcement: `step(keyword, text, /, **placeholders)`
# is the executable `with`-block CM. On entry it resolves the calling function
# (`sys._getframe(1).f_code.co_name` → `test_<slug>`) to a scenario in the
# cached feature index, tracks position via a frame-keyed counter, and verifies
# the block matches `scenario.steps[position]` on
# (keyword-case-insensitively, text, placeholder-name-set). On the first step
# of a scenario it also verifies any `@pytest.mark.parametrize(...)` decorator
# against the feature's Examples. On exception the CM appends
# `f"{keyword} {text}"` via PEP 678 `add_note` so failures attribute to their
# step. `keyword`/`text` are positional-only; placeholder values are
# consumer-supplied scalars, hence `object`.
class StepError(Exception): ...

@contextmanager
def step(
    keyword: str,
    text: str,
    /,
    **placeholders: object,
) -> Iterator[None]: ...
