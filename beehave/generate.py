from __future__ import annotations

import ast
import contextlib
import re
from pathlib import Path

from beehave.config import Config
from beehave.discover import discover_tests
from beehave.gherkin import GherkinError, parse_feature
from beehave.models import ScenarioInfo


def coerce_example_value(cell: str) -> object:
    if re.match(r"^-?\d+$", cell):
        return int(cell)
    if re.match(r"^-?\d+\.\d+$", cell):
        return float(cell)
    if cell.lower() == "true":
        return True
    if cell.lower() == "false":
        return False
    if cell.startswith('"') and cell.endswith('"'):
        return cell[1:-1]
    return cell


def _infer_strategy_from_examples(
    header: str,
    examples: object,
) -> str:
    from beehave.models import ExamplesTable

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
    config: Config,
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
        parts.append("settings")
        parts.append("strategies as st")

    if not parts:
        return []

    lines: list[str] = []
    lines.append(f"from hypothesis import {', '.join(parts)}")
    lines.append("")
    if needs_st and config.max_examples >= 0:
        lines.append(
            f'settings.register_profile("beehave", '
            f"max_examples={config.max_examples})"
        )
        lines.append('settings.load_profile("beehave")')
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


def generate_stubs(
    feature_path: str,
    config: Config,
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
    test_file.parent.mkdir(parents=True, exist_ok=True)

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
        needed.add("settings")
        needed.add("strategies as st")
    if any(s.is_outline for s in scenarios.values()):
        needed.add("example")

    if test_file.exists():
        source = test_file.read_text(encoding="utf-8")
        missing = needed - existing_imports
        if missing:
            source = _update_import_line(source, missing)

        if (
            "settings" in needed
            and 'settings.load_profile("beehave")' not in source
            and config.max_examples >= 0
        ):
            lines_list = source.split("\n")
            insert_idx = 0
            for i, line in enumerate(lines_list):
                if line.startswith("from hypothesis import"):
                    insert_idx = i + 1
                    break
            lines_list.insert(
                insert_idx,
                "",
            )
            lines_list.insert(
                insert_idx + 1,
                f'settings.register_profile("beehave", '
                f"max_examples={config.max_examples})",
            )
            lines_list.insert(
                insert_idx + 2,
                'settings.load_profile("beehave")',
            )
            source = "\n".join(lines_list)

        with open(test_file, "w", encoding="utf-8") as f:
            f.write(source.rstrip("\n") + "\n\n")
            for func in new_functions:
                f.write(func + "\n")
    else:
        import_block = _build_import_block(scenarios, config)
        with open(test_file, "w", encoding="utf-8") as f:
            for line in import_block:
                f.write(line + "\n")
            for func in new_functions:
                f.write(func + "\n")
