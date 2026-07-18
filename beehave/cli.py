from __future__ import annotations

import sys
from collections.abc import Sequence
from pathlib import Path

from beehave.check import check
from beehave.generate import generate
from beehave.status import status


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        return 2
    cmd = args[0]
    if cmd == "generate":
        generate(Path.cwd())
        return 0
    if cmd == "status":
        return status(Path.cwd())
    if cmd == "check":
        return _check_all(Path.cwd())
    return 2


def _check_all(root: Path) -> int:
    features_dir = root / "docs" / "features"
    if not features_dir.is_dir():
        return 1
    test_py_text = _read_test_py(root / "tests")
    for feature_path in sorted(features_dir.glob("*.feature")):
        if not check(feature_path.read_text(), test_py_text):
            return 1
    return 0


def _read_test_py(tests_dir: Path) -> str:
    if not tests_dir.is_dir():
        return ""
    return "\n".join(path.read_text() for path in sorted(tests_dir.glob("*_test.py")))
