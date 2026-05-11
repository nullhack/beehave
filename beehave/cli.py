import json
import os
import re
import sys
import unicodedata
from pathlib import Path

from beehave.traceability import parse_feature


def sync(feature_path):
    raise NotImplementedError


def generate(feature_name: str | None = None, json_output: bool = False) -> str | None:
    """Generate test stubs for orphan scenarios.

    Returns formatted output string (text or JSON).
    """
    feature_files = _discover_feature_files(feature_name)
    if feature_name is not None and not feature_files:
        return f"ERROR: docs/features/{feature_name}.feature not found"

    results: list[dict] = []

    for fpath in feature_files:
        try:
            with open(fpath) as f:
                text = f.read()
            scenarios = parse_feature(text)
        except Exception as exc:
            results.append(
                {
                    "file": fpath,
                    "action": "error",
                    "error": str(exc),
                }
            )
            continue

        # Get the feature file stem for test directory naming
        stem = Path(fpath).stem
        test_dir = str(Path("tests") / "features" / stem)
        test_file = str(Path(test_dir) / "default_test.py")

        orphans = [s for s in scenarios if s.id_tag is not None]

        if not orphans:
            results.append(
                {
                    "file": fpath,
                    "action": "skipped",
                    "reason": "no scenarios found",
                }
            )
            continue

        for scenario in orphans:
            results.append(
                _process_scenario(scenario, test_dir, test_file, json_output)
            )

    if json_output:
        return _format_json_output(results)
    return _format_text_output(results)


def _discover_feature_files(feature_name: str | None = None) -> list[str]:
    """Discover .feature files. If feature_name is given, find only that file."""
    features_dir = Path("docs") / "features"
    if feature_name is not None:
        target = features_dir / f"{feature_name}.feature"
        if not target.exists():
            print(f"ERROR: {target} not found")
            return []
        return [str(target)]
    if not features_dir.exists():
        return []
    return sorted(str(p) for p in features_dir.glob("*.feature"))


def _format_json_output(results: list) -> str:
    return json.dumps(results, indent=2)


def _format_text_output(results: list) -> str:
    lines: list[str] = []
    for r in results:
        action = r.get("action", "")
        fpath = r.get("file", "")
        if action == "skipped":
            lines.append(f"{fpath}: {r.get('reason', '')}")
        elif action == "error":
            lines.append(f"ERROR: {fpath}: {r.get('error', '')}")
        elif action == "created":
            lines.append(f"Created {r.get('test_file', '')} for @{r.get('id', '')}")
        elif action == "appended":
            lines.append(f"Appended to {r.get('test_file', '')}: @{r.get('id', '')}")
        elif action == "skipped_existing":
            lines.append(
                f"Skipped @{r.get('id', '')} (exists in {r.get('test_file', '')})"
            )
    return "\n".join(lines)


def _process_scenario(
    scenario, test_dir: str, test_file: str, json_output: bool
) -> dict:
    """Process a single orphan scenario: create or append test stub."""
    from beehave.cli import _ensure_test_directory, _generate_stub_content

    test_ids = _extract_test_id_strings(test_dir)
    sid = str(scenario.id_tag)

    if sid in test_ids:
        return {
            "file": test_file,
            "id": sid,
            "scenario": scenario.name.value,
            "action": "skipped_existing",
        }

    content = _generate_stub_content(
        scenario_name=scenario.name.value,
        scenario_id=sid,
        steps=[],
        examples=[],
    )

    test_path = Path(test_file)
    if test_path.exists():
        _append_function_stub(test_file, content, json_output)
        return {
            "file": test_file,
            "id": sid,
            "scenario": scenario.name.value,
            "action": "appended",
        }
    else:
        _ensure_test_directory(test_dir)
        test_path.write_text(content)
        return {
            "file": test_file,
            "id": sid,
            "scenario": scenario.name.value,
            "action": "created",
        }


def _append_function_stub(filepath: str, content: str, json_output: bool) -> None:
    """Append function to existing file. In non-interactive modes, auto-append."""
    with open(filepath) as f:
        existing = f.read()
    if _is_interactive() and not json_output:
        response = input(f"{filepath} already exists. Add function? [y/N] ")
        if response.lower() != "y":
            return
    with open(filepath, "w") as f:
        f.write(existing.rstrip() + "\n" + content)


def _to_snake_case(title: str) -> str:
    normalized = unicodedata.normalize("NFKD", title)
    stripped = "".join(c for c in normalized if not unicodedata.combining(c))
    replaced = re.sub(r"[^a-zA-Z0-9]", "_", stripped)
    collapsed = re.sub(r"_+", "_", replaced)
    trimmed = collapsed.strip("_")
    lowered = trimmed.lower()
    words = lowered.split("_")
    processed = []
    for word in words:
        if word and word[0].isdigit():
            processed.append("scenario_" + word)
        else:
            processed.append(word)
    result = "_".join(processed)
    if not result:
        result = "scenario"
    return result[:80]


def _build_function_name(scenario_name: str, scenario_id: str) -> str:
    snake = _to_snake_case(scenario_name)
    return f"test_{snake}_{scenario_id}"


def _generate_stub_content(
    scenario_name: str, scenario_id: str, steps: list, examples: list
) -> str:
    lines = []
    lines.append("from beehave.decorators import Given, When, Then, Example")
    lines.append("from hypothesis import strategies as st")
    lines.append("")
    lines.append("")
    lines.append("# Strategy variables")
    lines.append("default_strategy = st.integers()")
    lines.append("")
    lines.append("")
    for step_text in steps:
        step_type = step_text.split()[0]
        step_content = step_text[len(step_type) :].strip()
        decorator_map = {
            "Given": "Given",
            "When": "When",
            "Then": "Then",
            "And": "And",
            "But": "But",
        }
        decorator_name = decorator_map[step_type]
        step_snake = _to_snake_case(step_content)
        lines.append(f'@{decorator_name}("{step_content}")')
        lines.append(f"def step_{step_snake}():")
        lines.append("    ...")
        lines.append("")
        lines.append("")
    func_name = _build_function_name(scenario_name, scenario_id)
    lines.append(f"def {func_name}():")
    lines.append("    ...")
    lines.append("")
    return "\n".join(lines)


def _find_orphan_scenarios(feature_path: str, test_dir: str) -> list:
    with open(feature_path) as f:
        text = f.read()
    scenarios = parse_feature(text)
    test_ids = _extract_test_id_strings(test_dir)
    orphans = []
    for scenario in scenarios:
        if scenario.id_tag and str(scenario.id_tag) not in test_ids:
            orphans.append(scenario)
    return orphans


def _extract_test_id_strings(test_dir: str) -> set:
    func_pattern = re.compile(r"def (test_\w+)\s*\(")
    ids = set()
    test_path = Path(test_dir)
    if not test_path.exists():
        return ids
    for py_file in test_path.glob("**/*_test.py"):
        content = py_file.read_text()
        for match in func_pattern.finditer(content):
            func_name = match.group(1)
            parts = func_name.rsplit("_", 1)
            if len(parts) == 2 and len(parts[1]) == 8:
                ids.add(parts[1])
    return ids


def _ensure_test_directory(feature_name: str) -> str:
    os.makedirs(feature_name, exist_ok=True)
    return feature_name


def _is_interactive() -> bool:
    return sys.stdin.isatty()


def _append_function(filepath: str, content: str) -> None:
    with open(filepath) as f:
        existing = f.read()
    if _is_interactive():
        response = input(f"{filepath} already exists. Add function? [y/N] ")
        if response.lower() != "y":
            return
    with open(filepath, "w") as f:
        f.write(existing.rstrip() + "\n" + content)
