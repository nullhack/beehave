import hashlib
import re
import secrets
import string
from dataclasses import dataclass, field

_HEX_ID_PATTERN = re.compile(r"^[0-9a-f]{8}$")
_BEHAVE_ID_PATTERN = re.compile(r"^@id:([0-9a-f]{8})$")
_SECTION_BREAK_KEYWORDS = ("Example", "Scenario", "Rule", "Feature")


@dataclass(frozen=True)
class IdTag:
    value: str

    def __len__(self):
        return len(self.value)

    def __iter__(self):
        return iter(self.value)

    def __eq__(self, other):
        if isinstance(other, IdTag):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other
        return NotImplemented

    def __hash__(self):
        return hash(self.value)

    def __str__(self):
        return self.value

    def matches_pattern(self):
        value = self.value
        return bool(_HEX_ID_PATTERN.match(value))


@dataclass(frozen=True)
class ScenarioName:
    value: str


@dataclass(frozen=True)
class TestFunctionName:
    value: str


@dataclass(frozen=True)
class LineNumber:
    value: int


@dataclass(frozen=True)
class Placeholder:
    name: str
    is_string: bool = False


@dataclass(frozen=True)
class OrphanScenario:
    scenario_name: ScenarioName
    id_tag: IdTag

    def describe(self):
        return f"Scenario '{self.scenario_name.value}' (@id:{self.id_tag.value})"


@dataclass(frozen=True)
class OrphanTest:
    test_function_name: TestFunctionName
    id_tag: IdTag

    def describe(self):
        return f"Test '{self.test_function_name.value}' (@id:{self.id_tag.value})"


@dataclass
class OrphanScenarioList:
    items: list[OrphanScenario] = field(default_factory=list)

    def __getitem__(self, index):
        return self.items[index]

    def __len__(self):
        return len(self.items)

    def has_orphans(self):
        return len(self.items) > 0


@dataclass
class OrphanTestList:
    items: list[OrphanTest] = field(default_factory=list)

    def __getitem__(self, index):
        return self.items[index]

    def __len__(self):
        return len(self.items)

    def has_orphans(self):
        return len(self.items) > 0


@dataclass
class TraceabilityReport:
    orphan_scenarios: OrphanScenarioList = field(default_factory=OrphanScenarioList)
    orphan_tests: OrphanTestList = field(default_factory=OrphanTestList)

    def has_orphans(self):
        return self.orphan_scenarios.has_orphans() or self.orphan_tests.has_orphans()


@dataclass(frozen=True)
class Scenario:
    name: ScenarioName
    id_tag: IdTag | None
    placeholders: tuple[Placeholder, ...] = ()

    def has_identifier(self):
        return self.id_tag is not None


def generate_id() -> IdTag:
    chars = string.hexdigits[:16]
    value = "".join(secrets.choice(chars) for _ in range(8))
    return IdTag(value=value)


def parse_feature(text: str) -> list[Scenario]:
    lines = text.split("\n")
    return _extract_scenarios(lines)


def _extract_scenarios(lines: list[str]) -> list[Scenario]:
    scenarios: list[Scenario] = []
    for index, line in enumerate(lines):
        _try_append_scenario(lines, index, line.strip(), scenarios)
    return scenarios


def _derive_row_id(heading_id: IdTag | None, row_index: int) -> IdTag:
    """Derive a deterministic @id for an expanded Scenario Outline row."""
    raw = f"{heading_id.value}{row_index}" if heading_id is not None else f"{row_index}"
    value = hashlib.sha256(raw.encode()).hexdigest()[:8]
    return IdTag(value=value)


def _try_append_scenario(lines, index, stripped, scenarios):
    if not _is_scenario_heading(stripped):
        return
    name = _extract_scenario_name(stripped)
    example_rows = _count_example_rows(lines, index)
    placeholders = _extract_step_placeholders(lines, index)
    if example_rows > 1:
        heading_id = _find_preceding_identifier(lines, index)
        for row_index in range(example_rows):
            scenarios.append(
                Scenario(
                    name=ScenarioName(name),
                    id_tag=_derive_row_id(heading_id, row_index),
                    placeholders=placeholders,
                )
            )
    else:
        identifier = _find_preceding_identifier(lines, index)
        scenarios.append(
            Scenario(
                name=ScenarioName(name),
                id_tag=identifier,
                placeholders=placeholders,
            )
        )


def _extract_step_placeholders(lines, heading_index):
    seen = set()
    placeholders = []
    for i in range(heading_index + 1, len(lines)):
        stripped = lines[i].strip()
        if not stripped or stripped.startswith("#"):
            continue
        if _is_section_break(stripped) or stripped.startswith("Examples:"):
            break
        for match in re.finditer(r"<([^>]+)>", stripped):
            name = match.group(1)
            if name not in seen:
                seen.add(name)
                before = stripped[match.start() - 1 : match.start()]
                after = stripped[match.end() : match.end() + 1]
                is_string = before == "'" and after == "'"
                placeholders.append(Placeholder(name=name, is_string=is_string))
    return tuple(placeholders)


def _count_example_rows(lines, heading_index):
    """Count data rows in Examples table after a scenario heading."""
    for i in range(heading_index + 1, len(lines)):
        stripped = lines[i].strip()
        if stripped == "Examples:":
            return _count_data_rows(lines, i + 1)
        if _is_scenario_heading(stripped) or stripped.startswith(("Feature:", "Rule:")):
            return 0
    return 0


def _count_data_rows(lines, start):
    """Count pipe-delimited data rows (excluding header row)."""
    pipe_rows = 0
    for i in range(start, len(lines)):
        stripped = lines[i].strip()
        if stripped.startswith("|"):
            pipe_rows += 1
        elif stripped:
            break
    return max(0, pipe_rows - 1)


def _is_scenario_heading(stripped: str) -> bool:
    return stripped.startswith("Example:") or stripped.startswith("Scenario")


def _extract_scenario_name(stripped: str) -> str:
    return stripped.split(":", 1)[1].strip()


def _is_section_break(text: str) -> bool:
    return any(text.startswith(keyword) for keyword in _SECTION_BREAK_KEYWORDS)


def _find_preceding_identifier(lines, index):
    return _process_scan_line(lines, index)


def _process_scan_line(lines, index):
    for scan_index in range(index - 1, -1, -1):
        text = lines[scan_index].strip()
        if text.startswith("@id:"):
            return IdTag(value=text[4:].strip())
        if _is_section_break(text):
            return None
    return None


def check_traceability(feature_ids, test_ids):
    return _build_report(
        _find_orphan_scenarios(feature_ids, test_ids),
        _find_orphan_tests(feature_ids, test_ids),
    )


def _build_report(orphan_scenarios, orphan_tests):
    return TraceabilityReport(
        orphan_scenarios=OrphanScenarioList(items=orphan_scenarios),
        orphan_tests=OrphanTestList(items=orphan_tests),
    )


def _find_orphan_scenarios(
    feature_ids: list[str], test_ids: list[str]
) -> list[OrphanScenario]:
    test_set = set(test_ids)
    return [
        OrphanScenario(
            scenario_name=ScenarioName(feature_id), id_tag=IdTag(value=feature_id)
        )
        for feature_id in feature_ids
        if feature_id not in test_set
    ]


def _find_orphan_tests(feature_ids: list[str], test_ids: list[str]) -> list[OrphanTest]:
    feature_set = set(feature_ids)
    return [
        OrphanTest(
            test_function_name=TestFunctionName(test_id), id_tag=IdTag(value=test_id)
        )
        for test_id in test_ids
        if test_id not in feature_set
    ]


def sync(feature_path: str) -> None:
    content = _read_feature_file(feature_path)
    lines = content.split("\n")
    synced_lines = _sync_lines(lines)
    _write_feature_file(feature_path, synced_lines)


def _read_feature_file(path: str) -> str:
    with open(path) as file_handle:
        return file_handle.read()


def _write_feature_file(path: str, lines: list[str]) -> None:
    with open(path, "w") as file_handle:
        file_handle.write("\n".join(lines))


def _sync_lines(lines: list[str]) -> list[str]:
    synced: list[str] = []
    for index, line in enumerate(lines):
        synced = _process_line(lines, index, line, synced)
    return synced


def _process_line(lines, index, line, synced):
    if not _is_scenario_heading(line.strip()):
        synced.append(line)
        return synced
    return _handle_scenario_heading(lines, index, synced, line)


def _handle_scenario_heading(lines, index, synced, line):
    synced = _ensure_identifier(lines, index, synced)
    synced.append(line)
    return synced


def _ensure_identifier(lines, index, synced):
    if not _has_preceding_identifier(lines, index):
        new_identifier = generate_id()
        synced.append(_format_identifier_line(lines[index], new_identifier))
        return synced
    return _replace_if_malformed(lines, index, synced)


def _has_preceding_identifier(lines, index):
    if index == 0:
        return False
    return lines[index - 1].strip().startswith("@id:")


def _replace_if_malformed(lines, index, synced):
    if _BEHAVE_ID_PATTERN.match(lines[index - 1].strip()):
        return synced
    new_identifier = generate_id()
    synced[-1] = _format_identifier_line(lines[index - 1], new_identifier)
    return synced


def _format_identifier_line(source_line, identifier):
    indentation = _extract_leading_indent(source_line)
    return f"{indentation}@id:{identifier}"


def _extract_leading_indent(line: str) -> str:
    if not line:
        return ""
    return line[: len(line) - len(line.lstrip())]
