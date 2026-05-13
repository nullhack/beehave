from __future__ import annotations

import ast
import sys
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
        print(f"Error: Feature file not found: {fpath}", file=sys.stderr)
        raise SystemExit(1) from None

    try:
        scenarios = parse_feature(fpath, config)
    except GherkinError as e:
        print(f"Error: {e}", file=sys.stderr)
        raise SystemExit(1) from None

    if not scenarios:
        return

    feature_dir = next(iter(scenarios.values())).feature_path

    rule_paths = {si.rule_path for si in scenarios.values()}
    for rp in rule_paths:
        test_file = Path(config.tests_dir) / feature_dir / f"{rp}.py"
        if not test_file.exists():
            continue

        rp_scenarios = {fn: si for fn, si in scenarios.items() if si.rule_path == rp}
        tests = discover_tests(test_file)
        unmapped_fns = [fn for fn in tests if fn not in rp_scenarios]

        if not unmapped_fns:
            continue

        non_stub = [fn for fn in unmapped_fns if not tests[fn].is_stub]
        if non_stub and not force:
            for fn in non_stub:
                print(
                    f"Warning: '{fn}' is not a stub. "
                    f"Use --force to remove non-stub functions.",
                )
            continue

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
            continue

        new_source = ast.unparse(tree)
        test_file.write_text(new_source + "\n", encoding="utf-8")
        names = ", ".join(sorted(removed))
        print(
            f"Removed {len(removed)} unmapped function(s) "
            f"from {test_file.name}: {names}"
        )
