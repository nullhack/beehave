"""Test stub generator.

Reads a ``.feature`` file and produces corresponding pytest-beehave test stubs,
complete with Hypothesis strategies inferred from Examples tables and Gherkin
placeholders.
"""

from __future__ import annotations

import ast
import contextlib
import re
import sys
from pathlib import Path

from beehave.config import Config
from beehave.discover import discover_tests
from beehave.gherkin import GherkinError, parse_feature, validate_all_titles
from beehave.models import ExamplesTable, ScenarioInfo, coerce_example_value


def _infer_strategy_from_examples(
    header: str,
    examples: object,
) -> str:
    table: ExamplesTable = examples
    col_idx = table.headers.index(header)
    values = [row[col_idx] for row in table.rows]

    types: set[str] = set()
    for v in values:
        if re.match(r"^-?\d+$", v):
            types.add("integers")
        elif re.match(r"^-?\d+\.\d+$", v):
            types.add("floats")
        elif v.lower() in ("true", "false"):
            types.add("booleans")
        else:
            types.add("text")

    if types == {"integers"}:
        return "st.integers()"
    if types == {"floats"}:
        return "st.floats()"
    if types == {"booleans"}:
        return "st.booleans()"
    return "st.text()"


def _resolve_strategy(
    placeholder_name: str,
    scenario: ScenarioInfo,
    existing_strategies: set[str],
    config: Config,
) -> str:
    if placeholder_name in existing_strategies:
        return placeholder_name

    if (
        scenario.is_outline
        and scenario.examples
        and placeholder_name in scenario.examples.headers
    ):
        return _infer_strategy_from_examples(placeholder_name, scenario.examples)

    return config.default_strategy_expr


def _generate_function(
    scenario: ScenarioInfo,
    existing_strategies: set[str],
    config: Config,
) -> str:
    lines: list[str] = []

    has_params = bool(scenario.placeholders)

    if has_params:
        given_kwargs = []
        for ph in scenario.placeholders:
            strategy = _resolve_strategy(ph.name, scenario, existing_strategies, config)
            given_kwargs.append(f"{ph.name}={strategy}")

        if scenario.is_outline and scenario.examples:
            for row in scenario.examples.rows:
                row_parts = []
                for i, header in enumerate(scenario.examples.headers):
                    val = coerce_example_value(row[i])
                    if isinstance(val, str):
                        row_parts.append(f'{header}="{val}"')
                    elif isinstance(val, bool):
                        row_parts.append(f"{header}={val}")
                    else:
                        row_parts.append(f"{header}={val}")
                lines.append(f"@example({', '.join(row_parts)})")

        lines.append(f"@given({', '.join(given_kwargs)})")

        params = ", ".join(ph.name for ph in scenario.placeholders)
        lines.append(f"def {scenario.function_name}({params}):")
    else:
        lines.append(f"def {scenario.function_name}():")

    lines.append("    ...")
    lines.append("")
    return "\n".join(lines)


def _build_import_block(
    scenarios: dict[str, ScenarioInfo],
) -> list[str]:
    needs_given = any(s.placeholders for s in scenarios.values())
    needs_example = any(s.is_outline for s in scenarios.values())
    needs_st = needs_given

    parts: list[str] = []
    if needs_given:
        parts.append("given")
    if needs_example:
        parts.append("example")
    if needs_st:
        parts.append("strategies as st")

    if not parts:
        return []

    lines: list[str] = []
    lines.append(f"from hypothesis import {', '.join(parts)}")
    lines.append("")
    return lines


def _parse_existing_imports(source: str) -> set[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()

    imported: set[str] = set()
    for node in tree.body:
        if (
            isinstance(node, ast.ImportFrom)
            and node.module
            and "hypothesis" in node.module
        ):
            for alias in node.names:
                imported.add(alias.asname or alias.name)
    return imported


def _update_import_line(
    source: str,
    needed: set[str],
) -> str:
    lines = source.split("\n")
    for i, line in enumerate(lines):
        if not line.startswith("from hypothesis import"):
            continue

        current = line.replace("from hypothesis import", "").strip()
        current_set = {p.strip() for p in current.split(",")}
        current_set.update(needed)

        ordered: list[str] = []
        for name in ["given", "example", "settings"]:
            if name in current_set:
                ordered.append(name)
        if "strategies as st" in current_set:
            ordered.append("strategies as st")

        lines[i] = f"from hypothesis import {', '.join(ordered)}"
        break

    return "\n".join(lines)


def _write_file(
    test_file: Path,
    scenarios: dict[str, ScenarioInfo],
    config: Config,
) -> None:
    test_file.parent.mkdir(parents=True, exist_ok=True)
    init_file = test_file.parent / "__init__.py"
    if not init_file.exists():
        init_file.touch()

    existing_functions: set[str] = set()
    existing_strategies: set[str] = set()
    existing_imports: set[str] = set()

    if test_file.exists():
        with contextlib.suppress(Exception):
            existing_functions = set(discover_tests(test_file).keys())

        try:
            source = test_file.read_text(encoding="utf-8")
            existing_imports = _parse_existing_imports(source)
            tree = ast.parse(source)
            for node in tree.body:
                if (
                    isinstance(node, ast.Assign)
                    and len(node.targets) == 1
                    and isinstance(node.targets[0], ast.Name)
                ):
                    existing_strategies.add(node.targets[0].id)
        except SyntaxError:
            pass

    new_functions: list[str] = []
    for fn, scenario in scenarios.items():
        if fn not in existing_functions:
            new_functions.append(
                _generate_function(scenario, existing_strategies, config)
            )

    if not new_functions:
        return

    needed: set[str] = set()
    if any(s.placeholders for s in scenarios.values()):
        needed.add("given")
        needed.add("strategies as st")
    if any(s.is_outline for s in scenarios.values()):
        needed.add("example")

    if test_file.exists():
        source = test_file.read_text(encoding="utf-8")
        missing = needed - existing_imports
        if missing:
            source = _update_import_line(source, missing)

        with open(test_file, "w", encoding="utf-8") as f:
            f.write(source.rstrip("\n") + "\n\n")
            for func in new_functions:
                f.write(func + "\n")
    else:
        import_block = _build_import_block(scenarios)
        with open(test_file, "w", encoding="utf-8") as f:
            for line in import_block:
                f.write(line + "\n")
            for func in new_functions:
                f.write(func + "\n")


def generate_stubs(
    feature_path: str,
    config: Config,
) -> None:
    """Generate test stubs for a feature file.

    Runs ``validate_all_titles`` as a pre-flight gate: if any title in the
    project is invalid or duplicated, generation is refused.  Then parses the
    requested feature, builds import blocks, infers Hypothesis strategies from
    Examples tables and Gherkin placeholders, and writes the test stubs to
    ``tests/features/<feature_path>/``.

    Args:
        feature_path: The feature file stem (e.g. ``"hive_activity"``).
        config: The project configuration.

    Raises:
        SystemExit: When pre-flight title validation fails or the feature file
            does not exist.

    """
    violations = validate_all_titles(config)
    if violations:
        for v in violations:
            print(str(v), file=sys.stderr)
        raise SystemExit(1)

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

    rule_groups: dict[str, dict[str, ScenarioInfo]] = {}
    for fn, si in scenarios.items():
        rp = si.rule_path
        if rp not in rule_groups:
            rule_groups[rp] = {}
        rule_groups[rp][fn] = si

    for rp, group in rule_groups.items():
        test_file = Path(config.tests_dir) / feature_dir / f"{rp}.py"
        _write_file(test_file, group, config)
