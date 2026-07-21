# v3 superset check: derives expected `def test_<slug>(params) -> None` lines
# from the feature source, parses `py_text` AST for non-private top-level
# function signatures, and returns True iff the two sets are equal. Private
# functions (leading underscore) are exempt — part of the consumer's superset
# (helpers, fixtures). Non-private function signatures must match 1-1 in
# name, parameter names, parameter types, and order. The CLI additionally
# runs an orphan-module check (a `*_test.py` in `tests/features/` whose stem
# does not correspond to any feature's expected module is flagged).
def check(feature_text: str, py_text: str) -> bool: ...
