from __future__ import annotations

import os
import subprocess
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


def _run_stubtest(root: Path) -> bool:
    tests_features_dir = root / "tests" / "features"
    if not tests_features_dir.is_dir():
        return True
    modules = [p.stem for p in sorted(tests_features_dir.glob("*_test.py"))]
    if not modules:
        return True
    env = dict(os.environ)
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(tests_features_dir) + (
        os.pathsep + existing if existing else ""
    )
    existing_mypy = env.get("MYPYPATH", "")
    env["MYPYPATH"] = str(tests_features_dir) + (
        os.pathsep + existing_mypy if existing_mypy else ""
    )
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "mypy.stubtest",
            "--ignore-missing-stub",
            *modules,
        ],
        env=env,
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        sys.stdout.write(result.stdout)
        sys.stderr.write(result.stderr)
        return False
    return True


def _check_all(root: Path) -> int:
    features_dir = root / "docs" / "features"
    if not features_dir.is_dir():
        return 1
    tests_features_dir = root / "tests" / "features"
    if tests_features_dir.is_dir():
        orphans = [
            p
            for p in sorted(tests_features_dir.glob("*_test.py"))
            if not p.with_suffix(".pyi").exists()
        ]
        if orphans:
            for orphan in orphans:
                print(f"orphan: {orphan.name}", file=sys.stderr)
            return 1
    if not _run_stubtest(root):
        return 1
    stub_text = _read_stub_text(tests_features_dir)
    for feature_path in sorted(features_dir.glob("*.feature")):
        if not check(feature_path.read_text(), stub_text):
            return 1
    return 0


def _read_stub_text(tests_dir: Path) -> str:
    if not tests_dir.is_dir():
        return ""
    return "\n".join(path.read_text() for path in sorted(tests_dir.glob("*_test.pyi")))
