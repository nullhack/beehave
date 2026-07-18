from pathlib import Path

# Minimal `status` (journal Q3): prints `.feature` count under
# `<root>/docs/features/` and `*_test.pyi` count under `<root>/tests/` to
# stdout; returns 0 when the features directory exists, 2 when it is
# missing (filesystem error). v1's rich stage taxonomy / `--json` / tree
# output / unmapped-directory reporting are all dropped.
def status(root: Path) -> int: ...
