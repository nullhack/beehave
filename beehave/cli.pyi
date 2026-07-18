from collections.abc import Sequence

# CLI entry: `beehave generate|check|status`. Returns the process exit code
# (0 success; 2 missing features dir on `status`; non-zero on `check`
# structural-binding failure or when orphan `*_test.py` files without `.pyi`
# siblings are found in `<root>/tests/features/`). `argv` defaults to
# `sys.argv[1:]` when None.
def main(argv: Sequence[str] | None = None) -> int: ...
