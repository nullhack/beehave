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


_STEP_KEYWORDS = ("Given", "When", "Then", "And", "But")
_DECORATOR_RE = re.compile(r'@(Given|When|Then|And|But)\("(.*)"\)')
_FUNC_DEF_RE = re.compile(r"def (test_\w+)\s*\(([^)]*)\)")


def _parse_feature_steps(text: str) -> dict[str, list[tuple[str, str]]]:
    """Parse .feature text, return {id_tag: [(keyword, step_text), ...]}."""
    lines = text.split("\n")
    result: dict[str, list[tuple[str, str]]] = {}
    current_id: str | None = None
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("@id:"):
            current_id = stripped[4:]
        elif current_id:
            for kw in _STEP_KEYWORDS:
                if stripped.startswith(kw) and (
                    len(stripped) == len(kw) or stripped[len(kw)] == " "
                ):
                    step_text = stripped[len(kw) :].strip()
                    if current_id not in result:
                        result[current_id] = []
                    result[current_id].append((kw, step_text))
                    break
    return result


def _parse_test_decorators(test_dir: str) -> dict[str, dict]:
    """Parse test files, return {id_tag: {file, function_name, decorators, params}}."""
    result: dict[str, dict] = {}
    test_path = Path(test_dir)
    if not test_path.exists():
        return result
    for py_file in test_path.glob("**/*_test.py"):
        content = py_file.read_text()
        lines = content.split("\n")
        pending_decorators: list[tuple[str, str]] = []
        for line in lines:
            stripped = line.strip()
            dec_match = _DECORATOR_RE.search(stripped)
            if dec_match:
                pending_decorators.append((dec_match.group(1), dec_match.group(2)))
                continue
            func_match = _FUNC_DEF_RE.search(stripped)
            if func_match:
                func_name = func_match.group(1)
                params_str = func_match.group(2)
                parts = func_name.rsplit("_", 1)
                if len(parts) == 2 and len(parts[1]) == 8:
                    id_tag = parts[1]
                    result[id_tag] = {
                        "file": str(py_file),
                        "function_name": func_name,
                        "decorators": pending_decorators[:],
                        "params": params_str,
                    }
                pending_decorators = []
                continue
            if stripped and not stripped.startswith("@"):
                pending_decorators = []
    return result


def fix(feature_name: str | None = None, dry_run: bool = False) -> str | None:
    """Correct decorator text and add missing step decorators.

    Aligns test decorator strings with .feature step text, and adds
    missing decorators for steps that have no corresponding decorator.
    In dry-run mode, shows a diff of proposed changes without modifying files.
    """
    feature_files = _discover_feature_files(feature_name)
    diffs: list[str] = []
    for fpath in feature_files:
        stem = Path(fpath).stem
        test_dir = str(Path("tests") / "features" / stem)

        # Fix text mismatches
        mismatches = _find_text_mismatches(fpath, test_dir)
        for m in mismatches:
            file_path = m["file"]
            with open(file_path) as f:
                content = f.read()
            old_dec = f'@{m["keyword"]}("{m["old_text"]}")'
            new_dec = f'@{m["keyword"]}("{m["new_text"]}")'
            if dry_run:
                diffs.append(f"--- {file_path}\n+++ {file_path}")
                diffs.append(f"-{old_dec}")
                diffs.append(f"+{new_dec}")
            else:
                updated = content.replace(old_dec, new_dec)
                with open(file_path, "w") as f:
                    f.write(updated)

        # Add missing decorators
        additions = _add_missing_decorators(fpath, test_dir)
        for a in additions:
            file_path = a["file"]
            if dry_run:
                dec_line = f'@{a["keyword"]}("{a["step_text"]}")'
                diffs.append(f"--- {file_path}\n+++ {file_path}")
                diffs.append(f"+{dec_line}")
            else:
                with open(file_path) as f:
                    content = f.read()
                _insert_decorator_before_function(
                    file_path,
                    content,
                    a["function_name"],
                    a["keyword"],
                    a["step_text"],
                    a["params"],
                )

    if dry_run and diffs:
        return "\n".join(diffs)
    return None


def _insert_decorator_before_function(
    file_path: str,
    content: str,
    func_name: str,
    keyword: str,
    step_text: str,
    new_params: list[str],
) -> None:
    """Insert a decorator line before a function definition and add params."""
    lines = content.split("\n")
    result_lines: list[str] = []
    inserted = False
    for line in lines:
        if (
            not inserted
            and _FUNC_DEF_RE.search(line.strip())
            and func_name in _FUNC_DEF_RE.search(line.strip()).group(1)
        ):
            # Insert decorator before this function
            indent = line[: len(line) - len(line.lstrip())]
            result_lines.append(f'{indent}@{keyword}("{step_text}")')
            # Add new params to function signature
            new_line = _add_params_to_func(line, new_params)
            result_lines.append(new_line)
            inserted = True
            continue
        result_lines.append(line)
    with open(file_path, "w") as f:
        f.write("\n".join(result_lines))


def _add_params_to_func(func_line: str, new_params: list[str]) -> str:
    """Add new parameter names to a function definition line."""
    match = _FUNC_DEF_RE.search(func_line)
    if not match:
        return func_line
    existing_params_str = match.group(2).strip()
    existing_params = (
        [p.strip() for p in existing_params_str.split(",") if p.strip()]
        if existing_params_str
        else []
    )
    existing_set = set(existing_params)
    for p in new_params:
        if p not in existing_set:
            existing_params.append(p)
            existing_set.add(p)
    new_params_str = ", ".join(existing_params)
    return func_line.replace(f"({match.group(2)})", f"({new_params_str})")


def clean(feature_name: str | None = None, force: bool = False) -> None:
    """Remove orphan test functions that no longer match .feature scenarios.

    Prompts for interactive confirmation unless --force is given.
    """
    feature_files = _discover_feature_files(feature_name)
    for fpath in feature_files:
        stem = Path(fpath).stem
        test_dir = str(Path("tests") / "features" / stem)

        orphans = _find_orphan_tests(fpath, test_dir)
        if not orphans:
            continue

        # Group by file
        by_file: dict[str, list[str]] = {}
        for o in orphans:
            by_file.setdefault(o["file"], []).append(o["function_name"])

        total = len(orphans)
        if not force:
            if _is_interactive():
                response = input(f"Remove {total} orphan tests? [y/N] ")
                if response.lower() != "y":
                    return
            else:
                print(f"Found {total} orphan tests. Use --force to remove.")
                return

        for test_file, func_names in by_file.items():
            _remove_functions(test_file, func_names)


def _find_text_mismatches(feature_path: str, test_dir: str) -> list[dict]:
    """Find decorators whose text diverges from .feature step text."""
    with open(feature_path) as f:
        text = f.read()
    feature_steps = _parse_feature_steps(text)
    test_info = _parse_test_decorators(test_dir)

    mismatches: list[dict] = []
    for id_tag, steps in feature_steps.items():
        if id_tag not in test_info:
            continue
        info = test_info[id_tag]
        decorators = info["decorators"]
        for i, (_kw, step_text) in enumerate(steps):
            if i < len(decorators):
                dec_kw, dec_text = decorators[i]
                if dec_text != step_text:
                    mismatches.append(
                        {
                            "file": info["file"],
                            "function_name": info["function_name"],
                            "old_text": dec_text,
                            "new_text": step_text,
                            "keyword": dec_kw,
                        }
                    )
    return mismatches


def _add_missing_decorators(feature_path: str, test_dir: str) -> list[dict]:
    """Add step decorators for .feature steps missing from test code."""
    with open(feature_path) as f:
        text = f.read()
    feature_steps = _parse_feature_steps(text)
    test_info = _parse_test_decorators(test_dir)

    additions: list[dict] = []
    for id_tag, steps in feature_steps.items():
        if id_tag not in test_info:
            continue
        info = test_info[id_tag]
        decorators = info["decorators"]
        if len(steps) <= len(decorators):
            continue
        for i in range(len(decorators), len(steps)):
            kw, step_text = steps[i]
            placeholders = re.findall(r"<([^>]+)>", step_text)
            additions.append(
                {
                    "file": info["file"],
                    "function_name": info["function_name"],
                    "keyword": kw,
                    "step_text": step_text,
                    "params": placeholders,
                }
            )
    return additions


def _find_orphan_tests(feature_path: str, test_dir: str) -> list[dict]:
    """Find test functions whose @id has no match in .feature files."""
    with open(feature_path) as f:
        text = f.read()
    scenarios = parse_feature(text)
    feature_ids = {str(s.id_tag) for s in scenarios if s.id_tag is not None}
    test_info = _parse_test_decorators(test_dir)

    orphans: list[dict] = []
    for id_tag, info in test_info.items():
        if id_tag not in feature_ids:
            orphans.append(
                {
                    "file": info["file"],
                    "function_name": info["function_name"],
                    "id_tag": id_tag,
                }
            )
    return orphans


def _remove_functions(test_file: str, function_names: list[str]) -> None:
    """Remove named functions from a test file."""
    with open(test_file) as f:
        content = f.read()
    lines = content.split("\n")
    name_set = set(function_names)
    result_lines: list[str] = []
    skip_until_next_def = False

    for line in lines:
        stripped = line.strip()
        func_match = _FUNC_DEF_RE.search(stripped)
        if func_match:
            fname = func_match.group(1)
            if fname in name_set:
                skip_until_next_def = True
                # Remove preceding blank lines
                while result_lines and not result_lines[-1].strip():
                    result_lines.pop()
                continue
            skip_until_next_def = False
            result_lines.append(line)
        elif skip_until_next_def:
            if line and not line[0].isspace():
                skip_until_next_def = False
                result_lines.append(line)
        else:
            result_lines.append(line)

    # Clean trailing blank lines
    while result_lines and not result_lines[-1].strip():
        result_lines.pop()
    result_lines.append("")

    with open(test_file, "w") as f:
        f.write("\n".join(result_lines))


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
