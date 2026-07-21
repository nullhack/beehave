from collections.abc import Sequence

# CLI entry: `beehave generate|check [feature...]|status`. Returns the process
# exit code (0 success; 2 missing features dir on `status` or unknown command;
# non-zero on `check` superset failure). `argv` defaults to `sys.argv[1:]`
# when None.
#
# `beehave check` (no args): full sweep — reads every `docs/features/*.feature`,
# verifies each feature's expected scenario signatures exactly match the
# non-private top-level function signatures in the corresponding
# `tests/features/*_test.py` modules, and runs an orphan-module pass
# (`*_test.py` files whose stem doesn't correspond to any feature).
#
# `beehave check <path>...` (scoped): only the named `.feature` paths are
# parsed and checked. Skips orphan detection (which would require parsing
# every feature anyway, defeating the scoped fast-path). Consumers wire
# incremental scope themselves: `beehave check $(git diff --name-only HEAD~1
# HEAD -- docs/features/)`.
def main(argv: Sequence[str] | None = None) -> int: ...
