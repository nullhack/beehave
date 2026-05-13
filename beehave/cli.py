from __future__ import annotations

import argparse
from pathlib import Path

from beehave.check import check_all, check_single
from beehave.clean import clean_unmapped
from beehave.config import load_config
from beehave.generate import generate_stubs


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

    if violations:
        raise SystemExit(1)


def cmd_clean(args: argparse.Namespace) -> None:
    config = load_config()
    clean_unmapped(args.feature, config, force=args.force)


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

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
