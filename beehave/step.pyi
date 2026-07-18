from collections.abc import Iterator
from contextlib import contextmanager

# The v2 runtime core: `step(keyword, text, /, **placeholders)` is the
# executable `with` block that replaces v1's step-definition registry.
# `keyword` is data (covers all Gherkin keywords incl. localized); `assert`
# inside a `Then` block propagates; on exception the CM appends
# `f"{keyword} {text}"` via `add_note` so `__notes__ == ["<keyword> <text>"]`;
# no note on clean exit. `keyword`/`text` are positional-only; placeholder
# values are consumer-supplied scalars (strategy-inferred int/float/bool/str
# in emitted tests), so the kwarg type is `object`.
@contextmanager
def step(
    keyword: str,
    text: str,
    /,
    **placeholders: object,
) -> Iterator[None]: ...
