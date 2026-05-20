from __future__ import annotations

import argparse
import sys
from pathlib import Path

from beehave.check import check_all, check_single
from beehave.clean import clean_unmapped
from beehave.config import load_config
from beehave.discover import discover_tests
from beehave.generate import generate_stubs
from beehave.gherkin import GherkinError, parse_feature
from beehave.status import compute_status


def cmd_generate(args: argparse.Namespace) -> None:
    config = load_config()
    generate_stubs(args.feature, config)


def cmd_check(args: argparse.Namespace) -> None:
    config = load_config()
    if args.feature:
        fpath = Path(config.features_dir) / f"{args.feature}.feature"
        violations = check_single(fpath, config)
    else:
        violations = check_all(config)

    for v in violations:
        print(v)

    if any(not v.is_warning for v in violations):
        raise SystemExit(1)


def cmd_clean(args: argparse.Namespace) -> None:
    config = load_config()
    clean_unmapped(args.feature, config, force=args.force)


def cmd_list(args: argparse.Namespace) -> None:
    config = load_config()
    features_dir = Path(config.features_dir)
    if not features_dir.exists():
        return

    for feature_file in sorted(features_dir.rglob("*.feature")):
        try:
            scenarios = parse_feature(feature_file, config)
        except GherkinError as e:
            print(f"Error: {e}", file=sys.stderr)
            continue

        if not scenarios:
            continue

        feature_path = str(feature_file.relative_to(features_dir).with_suffix(""))
        title = next(iter(scenarios.values())).feature_title
        print(f"{feature_path}: {title}")

        if not args.verbose:
            continue

        print(f"  path: {feature_file}")
        print(f"  scenarios: {len(scenarios)}")

        rule_groups: dict[str, list[str]] = {}
        top_level: list[str] = []
        for fn, si in scenarios.items():
            if si.rule_path == "default_test":
                top_level.append(fn)
            else:
                rule_name = si.rule_path.removesuffix("_test")
                rule_groups.setdefault(rule_name, []).append(fn)

        if top_level:
            print(f"  top-level: {len(top_level)}")
        for rule_name, fns in rule_groups.items():
            print(f"  rules: {rule_name} ({len(fns)})")

        test_dir = Path(config.tests_dir) / next(iter(scenarios.values())).feature_path
        stub_count = 0
        impl_count = 0
        for si in scenarios.values():
            tf = test_dir / f"{si.rule_path}.py"
            tests = discover_tests(tf)
            ti = tests.get(si.function_name)
            if ti is not None and not ti.is_stub:
                impl_count += 1
            else:
                stub_count += 1
        total = stub_count + impl_count
        if impl_count == 0:
            print(f"  stubs: {total}/{total} (all stubs)")
        elif stub_count == 0:
            print(f"  stubs: 0/{total} (all implemented)")
        else:
            print(f"  stubs: {stub_count}/{total} ({impl_count} implemented)")


def cmd_status(args: argparse.Namespace) -> None:
    config = load_config()
    compute_status(
        config,
        json_output=args.json,
        include_unmapped=args.include_unmapped,
    )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="beehave",
        description="BDD living documentation in sync",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    gen = subparsers.add_parser(
        "generate",
        help="Generate test stubs from a feature file",
    )
    gen.add_argument(
        "feature",
        help=("Feature path without extension, relative to features_dir"),
    )
    gen.set_defaults(func=cmd_generate)

    chk = subparsers.add_parser(
        "check",
        help="Check consistency between features and tests",
    )
    chk.add_argument(
        "feature",
        nargs="?",
        default=None,
        help=("Feature path (optional; checks all if omitted)"),
    )
    chk.set_defaults(func=cmd_check)

    cln = subparsers.add_parser(
        "clean",
        help="Remove unmapped test functions",
    )
    cln.add_argument(
        "feature",
        help="Feature path without extension",
    )
    cln.add_argument(
        "--force",
        action="store_true",
        help="Remove non-stub functions without warning",
    )
    cln.set_defaults(func=cmd_clean)

    lst = subparsers.add_parser(
        "list",
        help="List all features with their paths",
    )
    lst.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show scenario counts, rules, and stub status",
    )
    lst.set_defaults(func=cmd_list)

    sts = subparsers.add_parser(
        "status",
        help="Show development status of all features",
    )
    sts.add_argument(
        "--json",
        action="store_true",
        help="Output status report as JSON",
    )
    sts.add_argument(
        "--include-unmapped",
        action="store_true",
        help="Report test directories with no matching feature file",
    )
    sts.set_defaults(func=cmd_status)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
