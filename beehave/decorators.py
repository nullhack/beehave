import re
import sys

from hypothesis import example as hypothesis_example
from hypothesis import given, settings
from hypothesis import strategies as st

_STEP_TYPES = ("Given", "When", "Then")
_PLACEHOLDER_RE = re.compile(r"<([^>]+)>")


class _BeehaveExample:
    __slots__ = ("args", "kwargs")

    def __init__(self, args, kwargs):
        self.args = args
        self.kwargs = kwargs

    def apply_to(self, function):
        return hypothesis_example(*self.args, **self.kwargs)(function)


def _caller_module_globals():
    return sys._getframe(1).f_globals


def _is_strategy(obj):
    return obj is not None and hasattr(obj, "filter") and hasattr(obj, "map")


def _resolve_placeholder(name, caller_module, examples=None):
    if examples and name in examples:
        return st.from_type(type(examples[name]))
    candidate = getattr(caller_module, name, None)
    if _is_strategy(candidate):
        return candidate
    return st.integers()


def _attach_step(func, step_type, step_text):
    steps = list(getattr(func, "__beehave_steps__", []))
    steps.append((step_type, step_text))
    func.__beehave_steps__ = steps
    return func


def _step_type_or_default(resolved):
    for prev_type, _ in reversed(resolved):
        if prev_type in _STEP_TYPES:
            return prev_type
    return "Given"


def _find_preceding_step_type(resolved):
    return _step_type_or_default(resolved)


def _resolve_step_type(step_type, resolved):
    if step_type in ("And", "But"):
        return _find_preceding_step_type(resolved)
    return step_type


def _resolve_continuations(steps):
    resolved = []
    for step_type, step_text in steps:
        resolved.append((_resolve_step_type(step_type, resolved), step_text))
    return resolved


def _get_reversed_resolved_steps(func):
    steps = list(getattr(func, "__beehave_steps__", []))
    steps.reverse()
    return _resolve_continuations(steps)


def _collect_placeholder_names(steps):
    all_names = []
    for _, text in steps:
        all_names.extend(_PLACEHOLDER_RE.findall(text))
    return list(dict.fromkeys(all_names))


def _resolve_all_strategies(names, caller_module, examples):
    return {name: _resolve_placeholder(name, caller_module, examples) for name in names}


def _apply_examples(function, beehave_examples):
    for example in reversed(beehave_examples):
        function = example.apply_to(function)
    return function


def _apply_hypothesis_wiring(function, strategies):
    function = given(**strategies)(function)
    return settings(max_examples=1)(function)


def _preserve_metadata(function, steps, examples):
    function.__beehave_steps__ = steps
    function.__beehave_examples__ = examples
    return function


def _apply_given(func, caller_module, examples=None):
    steps = _get_reversed_resolved_steps(func)
    beehave_egs = list(getattr(func, "__beehave_examples__", []))
    names = _collect_placeholder_names(steps)
    strategies = _resolve_all_strategies(names, caller_module, examples)
    return _preserve_metadata(
        _apply_hypothesis_wiring(_apply_examples(func, beehave_egs), strategies),
        steps,
        beehave_egs,
    )


def Given(step_text):  # noqa: N802
    caller_module = _caller_module_globals()

    def decorator(func):
        func = _attach_step(func, "Given", step_text)
        return _apply_given(func, caller_module)

    return decorator


def When(step_text):  # noqa: N802
    def decorator(func):
        return _attach_step(func, "When", step_text)

    return decorator


def Then(step_text):  # noqa: N802
    def decorator(func):
        return _attach_step(func, "Then", step_text)

    return decorator


def And(step_text):  # noqa: N802
    def decorator(func):
        return _attach_step(func, "And", step_text)

    return decorator


def But(step_text):  # noqa: N802
    def decorator(func):
        return _attach_step(func, "But", step_text)

    return decorator


def Example(*args, **kwargs):  # noqa: N802
    def decorator(func):
        examples = list(getattr(func, "__beehave_examples__", []))
        examples.append(_BeehaveExample(args, kwargs))
        func.__beehave_examples__ = examples
        return func

    return decorator


def Background(fixture):  # noqa: N802
    def decorator(func):
        background_steps = list(getattr(fixture, "__beehave_steps__", []))
        own_steps = list(getattr(func, "__beehave_steps__", []))
        func.__beehave_steps__ = background_steps + own_steps
        return func

    return decorator
