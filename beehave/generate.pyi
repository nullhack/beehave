from pathlib import Path

# Emits `<feature_slug>_default_test.py` plus one
# `<feature_slug>_<rule_slug>_test.py` per Rule into `<root>/tests/features/`,
# reading `<root>/docs/features/*.feature`. Emits `.py` skeleton only when
# absent (idempotent — never clobbers consumer bodies). Background steps
# (Feature-level and Rule-level) are prepended to the relevant scenarios'
# `with step(...)` block lists in the emitted `.py`. Scenario Outline Examples
# are emitted as a `@pytest.mark.parametrize(...)` decorator over the test
# function (string rows, all params typed `str`).
def generate(root: Path) -> None: ...
