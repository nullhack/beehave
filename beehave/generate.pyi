from pathlib import Path

# Emits `<feature_slug>_default_test.py{i,}` plus one
# `<feature_slug>_<rule_slug>_test.py{i,}` per Rule into `<root>/tests/features/`,
# reading `<root>/docs/features/*.feature`. Wipes stale `*_test.pyi` in the emit
# dir before writing. Always emits `.pyi`; emits `.py` skeleton only when absent
# (idempotent — never clobbers consumer bodies). Background steps (Feature-level
# and Rule-level) are prepended to the relevant scenarios' `with step(...)`
# block lists in the emitted `.py`.
def generate(root: Path) -> None: ...
