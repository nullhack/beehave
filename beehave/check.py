"""Feature-to-test consistency checker.

Verifies that every scenario has a matching test function with the correct
placeholders, literals, and example-table bijection.  Also runs global title
validation across all ``.feature`` files.
"""

from __future__ import annotations

import sys
from pathlib import Path

from beehave.config import Config
from beehave.discover import (
    DiscoverError,
    discover_tests,
    discover_tests_dir_with_paths,
)
from beehave.gherkin import GherkinError, parse_feature, validate_all_titles
from beehave.models import ScenarioInfo, TestInfo, Violation, coerce_example_value


def _check_placeholders(
    si: ScenarioInfo,
    ti: TestInfo,
    test_path: str,
) -> list[Violation]:
    """Verify every Gherkin placeholder appears in the test body.

    Placeholders are matched case-insensitively (``<Prefix>`` matches
    ``prefix`` in the test body).

    Args:
        si: Parsed scenario information.
        ti: Discovered test info.
        test_path: Path to the test file for error reporting.

    Returns:
        A list of ``Violation`` objects for each missing placeholder.

    """
    if ti.is_stub:
        return []

    violations: list[Violation] = []
    for ph in si.placeholders:
        if ph.name.lower() not in {n.lower() for n in ti.body_name_nodes}:
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
    """Verify every Gherkin step literal appears in the test body.

    Literal values are matched case-insensitively (``"Hello"`` matches
    ``"hello"`` in the test body).  Numeric literals are converted to
    strings before comparison.

    Args:
        si: Parsed scenario information.
        ti: Discovered test info.
        test_path: Path to the test file for error reporting.

    Returns:
        A list of ``Violation`` objects for each missing literal.

    """
    if ti.is_stub:
        return []

    violations: list[Violation] = []
    for lit in si.literals:
        lowered_constants = {str(c).lower() for c in ti.body_constant_nodes}
        if str(lit.value).lower() not in lowered_constants:
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
    """Check a single scenario against its test function.

    Validates that the test exists, that every Gherkin placeholder appears in
    the test body, that every string/numeric literal in the test has a
    corresponding Gherkin step token, and that ``@example`` decorators match
    Examples table rows.

    Args:
        si: Parsed scenario information.
        ti: Discovered test info, or ``None`` if no test was found.
        test_path: Path to the test file (for error reporting).
        feature_path: Path to the feature file (for error reporting).

    Returns:
        A list of ``Violation`` objects (empty if everything matches).

    """
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


def _scan_unmapped_tests(
    all_test_files: dict[str, dict[str, TestInfo]],
    scenarios: dict[str, ScenarioInfo],
    test_dir: Path,
) -> list[Violation]:
    violations: list[Violation] = []
    for rp, tests in all_test_files.items():
        test_file = test_dir / f"{rp}.py"
        for fn, ti in tests.items():
            si = scenarios.get(fn)
            if si is None:
                violations.append(
                    Violation(
                        path=str(test_file),
                        line=ti.line,
                        error_type="unmapped-test",
                        message=f"'{fn}' has no matching scenario",
                    )
                )
            elif si.rule_path != rp:
                violations.append(
                    Violation(
                        path=str(test_file),
                        line=ti.line,
                        error_type="misplaced-test",
                        message=(
                            f"'{fn}' is in {rp}.py but should be in {si.rule_path}.py"
                        ),
                        is_warning=True,
                    )
                )
    return violations


def check_single(
    feature_path: Path,
    config: Config,
) -> list[Violation]:
    """Check a single feature file against its test directory.

    Parses the feature, discovers the corresponding test files, and runs
    ``check_pair`` for every scenario.

    Args:
        feature_path: Path to a ``.feature`` file.
        config: The project configuration.

    Returns:
        A list of ``Violation`` objects.

    """
    try:
        scenarios = parse_feature(feature_path, config)
    except GherkinError as e:
        print(f"Error: {e}", file=sys.stderr)
        return []

    if not scenarios:
        return []

    first = next(iter(scenarios.values()))
    feature_dir = first.feature_path
    feature_rel = str(feature_path)

    scenario_by_rule: dict[str, dict[str, ScenarioInfo]] = {}
    for fn, si in scenarios.items():
        scenario_by_rule.setdefault(si.rule_path, {})[fn] = si

    test_dir = Path(config.tests_dir) / feature_dir
    all_test_files: dict[str, dict[str, TestInfo]] = {}
    if test_dir.exists():
        for py_file in sorted(test_dir.glob("*_test.py")):
            rp = py_file.stem
            try:
                all_test_files[rp] = discover_tests(py_file)
            except DiscoverError as e:
                print(f"Error: {e}", file=sys.stderr)
                all_test_files[rp] = {}

    violations: list[Violation] = []
    violations.extend(_scan_unmapped_tests(all_test_files, scenarios, test_dir))

    for fn, si in scenarios.items():
        test_file = test_dir / f"{si.rule_path}.py"
        rp_tests = all_test_files.get(si.rule_path, {})
        ti = rp_tests.get(fn)
        violations.extend(check_pair(si, ti, str(test_file), feature_rel))

    return violations


def check_all(config: Config) -> list[Violation]:
    """Run the full project-wide consistency check.

    Parses every ``.feature`` file, discovers every test function, and then
    for each scenario verifies placeholder coverage, literal mapping, example
    bijection, file placement, and orphan tests.  Finally runs
    ``validate_all_titles`` to catch title-level problems.

    Args:
        config: The project configuration.

    Returns:
        A consolidated list of every ``Violation`` found.

    """
    features_dir = Path(config.features_dir)
    if not features_dir.exists():
        print(
            f"Error: features directory '{config.features_dir}' not found",
            file=sys.stderr,
        )
        return []

    all_scenarios: dict[str, ScenarioInfo] = {}
    feature_paths: dict[str, Path] = {}

    seen_fn: dict[str, str] = {}
    for feature_file in sorted(features_dir.rglob("*.feature")):
        try:
            scenarios = parse_feature(
                feature_file,
                config,
                seen_function_names=seen_fn,
                skip_title_validation=True,
            )
        except GherkinError as e:
            print(f"Error: {e}", file=sys.stderr)
            continue
        for fn in scenarios:
            feature_paths[fn] = feature_file
        all_scenarios.update(scenarios)

    tests_dir = Path(config.tests_dir)
    test_file_map = discover_tests_dir_with_paths(tests_dir)

    violations: list[Violation] = []
    for fn, si in all_scenarios.items():
        feature_rel = str(feature_paths[fn])
        test_file = Path(config.tests_dir) / si.feature_path / f"{si.rule_path}.py"
        entry = test_file_map.get(fn)
        ti = entry[0] if entry else None
        violations.extend(check_pair(si, ti, str(test_file), feature_rel))

    for fn, (ti, test_file) in test_file_map.items():
        si = all_scenarios.get(fn)
        if si is None:
            violations.append(
                Violation(
                    path=str(test_file),
                    line=ti.line,
                    error_type="unmapped-test",
                    message=f"'{fn}' has no matching scenario",
                )
            )
        else:
            expected = Path(config.tests_dir) / si.feature_path / f"{si.rule_path}.py"
            if test_file.resolve() != expected.resolve():
                violations.append(
                    Violation(
                        path=str(test_file),
                        line=ti.line,
                        error_type="misplaced-test",
                        message=(
                            f"'{fn}' is in {test_file.name} "
                            f"but should be in {expected.name}"
                        ),
                        is_warning=True,
                    )
                )

    violations.extend(validate_all_titles(config))

    return violations
