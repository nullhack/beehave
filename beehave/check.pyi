# Structural binding check (L2 *Validation (`check`)*): the
# `with step(...)` blocks in `test_py_text` are matched one-to-one against
# the steps parsed from `feature_text` on the triple
# (keyword-case-insensitively, text, placeholder-name-set). Returns True if
# every block matches its step; False on any count, keyword, text, or
# placeholder-name-set mismatch. Does NOT inspect the body for literals or
# placeholder AST nodes (v2 drops that layer entirely — Q5). For Scenario
# Outlines, additionally requires a `@pytest.mark.parametrize(...)` decorator
# whose arg-names and rows round-trip the feature's Examples table; missing or
# mismatched parametrize returns False.
def check(feature_text: str, test_py_text: str) -> bool: ...
