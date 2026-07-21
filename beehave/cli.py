from __future__ import annotations

import sys
from collections.abc import Sequence
from pathlib import Path

from beehave.check import check
from beehave.generate import _slug_from, generate
from beehave.gherkin import Rule, parse_feature
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
        return _check_all(Path.cwd(), args[1:])
    return 2


def _feature_module_stems(feature_path: Path) -> list[str]:
    feature = parse_feature(feature_path.read_text())
    feature_slug = _slug_from(feature_path.stem)
    stems: list[str] = []
    has_default = any(not isinstance(c, Rule) for c in feature.children)
    if has_default:
        stems.append(f"{feature_slug}_default")
    for child in feature.children:
        if isinstance(child, Rule):
            stems.append(f"{feature_slug}_{_slug_from(child.name)}")
    return stems


def _resolve_feature_arg(root: Path, arg: str) -> Path | None:
    p = Path(arg)
    if not p.is_absolute():
        p = root / p
    if p.suffix != ".feature" or not p.exists():
        return None
    return p


def _check_all(root: Path, feature_args: list[str] | None = None) -> int:
    features_dir = root / "docs" / "features"
    if not features_dir.is_dir():
        return 1
    tests_features_dir = root / "tests" / "features"

    if feature_args:
        feature_paths: list[Path] = []
        for arg in feature_args:
            resolved = _resolve_feature_arg(root, arg)
            if resolved is None:
                print(f"not a feature file: {arg}", file=sys.stderr)
                return 1
            feature_paths.append(resolved)
    else:
        feature_paths = sorted(features_dir.glob("*.feature"))
        if tests_features_dir.is_dir():
            expected_stems: set[str] = set()
            for feature_path in feature_paths:
                expected_stems.update(_feature_module_stems(feature_path))
            actual_stems = {
                p.name.removesuffix("_test.py")
                for p in tests_features_dir.glob("*_test.py")
            }
            orphan_stems = sorted(actual_stems - expected_stems)
            if orphan_stems:
                for stem in orphan_stems:
                    print(f"orphan: {stem}_test.py", file=sys.stderr)
                return 1

    for feature_path in feature_paths:
        stems = _feature_module_stems(feature_path)
        py_text = "\n".join(
            (tests_features_dir / f"{stem}_test.py").read_text()
            for stem in stems
            if tests_features_dir.is_dir()
            and (tests_features_dir / f"{stem}_test.py").exists()
        )
        if not check(feature_path.read_text(), py_text):
            return 1
    return 0
