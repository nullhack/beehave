from __future__ import annotations

from pathlib import Path

from beehave.config import Config
from beehave.discover import DiscoverError, discover_tests, discover_tests_dir
from beehave.generate import coerce_example_value
from beehave.gherkin import GherkinError, parse_feature
from beehave.models import ScenarioInfo, TestInfo, Violation


def _check_placeholders(
    si: ScenarioInfo,
    ti: TestInfo,
    test_path: str,
) -> list[Violation]:
    if ti.is_stub:
        return []

    violations: list[Violation] = []
    for ph in si.placeholders:
        found = ph.name in ti.body_name_nodes or ph.name in ti.given_kwargs
        if not found:
            violations.append(
                Violation(
                    path=test_path,
                    line=ti.line,
                    error_type="missing-placeholder",
                    message=f"'{ph.name}' not found in function body",
                )
            )
    return violations


def _check_literals(
    si: ScenarioInfo,
    ti: TestInfo,
    test_path: str,
) -> list[Violation]:
    if ti.is_stub:
        return []

    violations: list[Violation] = []
    for lit in si.literals:
        if lit.value not in ti.body_constant_nodes:
            violations.append(
                Violation(
                    path=test_path,
                    line=ti.line,
                    error_type="missing-literal",
                    message=f"literal {lit.raw!r} not found in function body",
                )
            )
    return violations


def _check_examples_bijection(
    si: ScenarioInfo,
    ti: TestInfo,
    test_path: str,
    feature_path: str,
) -> list[Violation]:
    if not si.is_outline or si.examples is None or ti.is_stub:
        return []

    feature_rows: list[dict[str, object]] = []
    for row in si.examples.rows:
        row_dict: dict[str, object] = {}
        for i, header in enumerate(si.examples.headers):
            row_dict[header] = coerce_example_value(row[i])
        feature_rows.append(row_dict)

    test_rows = list(ti.example_rows)
    matched_test: set[int] = set()
    matched_feature: set[int] = set()

    for fi, frow in enumerate(feature_rows):
        for ti_idx, trow in enumerate(test_rows):
            if ti_idx in matched_test:
                continue
            if frow == trow:
                matched_feature.add(fi)
                matched_test.add(ti_idx)
                break

    violations: list[Violation] = []
    for fi in range(len(feature_rows)):
        if fi not in matched_feature:
            violations.append(
                Violation(
                    path=feature_path,
                    line=0,
                    error_type="example-mismatch",
                    message=(
                        f"Examples row {fi + 1} has no matching @example() decorator"
                    ),
                )
            )

    for ti_idx in range(len(test_rows)):
        if ti_idx not in matched_test:
            violations.append(
                Violation(
                    path=test_path,
                    line=0,
                    error_type="example-mismatch",
                    message="@example() decorator has no matching Examples row",
                )
            )

    return violations


def check_pair(
    si: ScenarioInfo,
    ti: TestInfo | None,
    test_path: str,
    feature_path: str,
) -> list[Violation]:
    violations: list[Violation] = []

    if ti is None:
        violations.append(
            Violation(
                path=feature_path,
                line=si.line,
                error_type="unmapped-scenario",
                message=f"scenario '{si.title}' has no test function",
            )
        )
        return violations

    violations.extend(_check_placeholders(si, ti, test_path))
    violations.extend(_check_literals(si, ti, test_path))
    violations.extend(_check_examples_bijection(si, ti, test_path, feature_path))
    return violations


def check_single(
    feature_path: Path,
    config: Config,
) -> list[Violation]:
    try:
        scenarios = parse_feature(feature_path, config)
    except GherkinError as e:
        print(f"Error: {e}")
        return []

    first = next(iter(scenarios.values())) if scenarios else None
    if first is None:
        return []

    feature_dir = first.feature_path
    test_file = Path(config.tests_dir) / feature_dir / "default_test.py"
    feature_rel = str(feature_path)

    try:
        tests = discover_tests(test_file)
    except DiscoverError as e:
        print(f"Error: {e}")
        return []

    violations: list[Violation] = []
    for fn, si in scenarios.items():
        ti = tests.get(fn)
        violations.extend(check_pair(si, ti, str(test_file), feature_rel))

    for fn, ti in tests.items():
        if fn not in scenarios:
            violations.append(
                Violation(
                    path=str(test_file),
                    line=ti.line,
                    error_type="unmapped-test",
                    message=f"'{fn}' has no matching scenario",
                )
            )

    return violations


def check_all(config: Config) -> list[Violation]:
    features_dir = Path(config.features_dir)
    if not features_dir.exists():
        print(f"Error: features directory '{config.features_dir}' not found")
        return []

    all_scenarios: dict[str, ScenarioInfo] = {}
    feature_paths: dict[str, Path] = {}

    seen_fn: dict[str, str] = {}
    for feature_file in sorted(features_dir.glob("*.feature")):
        try:
            scenarios = parse_feature(feature_file, config, seen_function_names=seen_fn)
        except GherkinError as e:
            print(f"Error: {e}")
            continue
        for fn in scenarios:
            feature_paths[fn] = feature_file
        all_scenarios.update(scenarios)

    tests_dir = Path(config.tests_dir)
    all_tests = discover_tests_dir(tests_dir)

    violations: list[Violation] = []
    for fn, si in all_scenarios.items():
        feature_rel = str(feature_paths[fn])
        test_file = Path(config.tests_dir) / si.feature_path / "default_test.py"
        ti = all_tests.get(fn)
        violations.extend(check_pair(si, ti, str(test_file), feature_rel))

    for fn, ti in all_tests.items():
        if fn not in all_scenarios:
            violations.append(
                Violation(
                    path=str(tests_dir),
                    line=ti.line,
                    error_type="unmapped-test",
                    message=f"'{fn}' has no matching scenario",
                )
            )

    return violations
