import os
import re
import sys
import unicodedata
from pathlib import Path

from beehave.traceability import parse_feature


def sync(feature_path):
    raise NotImplementedError


def generate(feature_name: str | None = None, json_output: bool = False) -> None:
    raise NotImplementedError


def _discover_feature_files(feature_name: str | None = None) -> list:
    raise NotImplementedError


def _format_json_output(results: list) -> str:
    raise NotImplementedError


def _format_text_output(results: list) -> str:
    raise NotImplementedError


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
