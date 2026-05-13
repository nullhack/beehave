from __future__ import annotations

import ast
from pathlib import Path

from beehave.config import Config
from beehave.discover import discover_tests
from beehave.gherkin import GherkinError, parse_feature


def clean_unmapped(
    feature_path: str,
    config: Config,
    force: bool = False,
) -> None:
    fpath = Path(config.features_dir) / f"{feature_path}.feature"
    if not fpath.exists():
        print(f"Error: Feature file not found: {fpath}")
        raise SystemExit(1) from None

    try:
        scenarios = parse_feature(fpath, config)
    except GherkinError as e:
        print(f"Error: {e}")
        raise SystemExit(1) from None

    if not scenarios:
        return

    feature_dir = next(iter(scenarios.values())).feature_path
    test_file = Path(config.tests_dir) / feature_dir / "default_test.py"

    if not test_file.exists():
        return

    tests = discover_tests(test_file)
    unmapped_fns = [fn for fn in tests if fn not in scenarios]

    if not unmapped_fns:
        return

    non_stub = [fn for fn in unmapped_fns if not tests[fn].is_stub]
    if non_stub and not force:
        for fn in non_stub:
            print(
                f"Warning: '{fn}' is not a stub. "
                f"Use --force to remove non-stub functions.",
            )
        return

    source = test_file.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(test_file))

    removed: set[str] = set()
    tree.body = [
        node
        for node in tree.body
        if not (
            isinstance(node, ast.FunctionDef)
            and node.name in unmapped_fns
            and not removed.add(node.name)
        )
    ]

    if not removed:
        return

    new_source = ast.unparse(tree)
    test_file.write_text(new_source + "\n", encoding="utf-8")
    print(f"Removed {len(removed)} unmapped function: {', '.join(sorted(removed))}")
