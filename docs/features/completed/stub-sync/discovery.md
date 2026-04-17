# Discovery: stub-sync

## State
Status: BASELINED

## Entities
| Type | Name | Candidate Class/Method | In Scope |
|------|------|----------------------|----------|
| Noun | test stub | generated `test_<feature>_<hex>()` function | Yes |
| Noun | test file | `tests/features/<feature>/<story>_test.py` | Yes |
| Noun | feature slug | underscored folder name used in function names | Yes |
| Noun | story slug | `.feature` file stem used as test file name | Yes |
| Noun | docstring | step-by-step docstring in test stub | Yes |
| Noun | step | individual Gherkin step (Given/When/Then/And/But) | Yes |
| Noun | orphan test | test function with no matching `@id` in any `.feature` | Yes |
| Noun | backlog stage | `docs/features/backlog/` | Yes |
| Noun | in-progress stage | `docs/features/in-progress/` | Yes |
| Noun | completed stage | `docs/features/completed/` — excluded from stub sync | Yes |
| Verb | create stub | write new test function for new Example | Yes |
| Verb | update docstring | replace docstring to match current steps | Yes |
| Verb | rename function | update function name if feature slug changed | Yes |
| Verb | mark orphan | add `@pytest.mark.skip(reason="orphan: ...")` | Yes |
| Verb | build all-steps docstring | include every step line (Given/When/Then/And/But) | Yes |

## Rules
- Only `backlog/` and `in-progress/` feature folders receive full stub sync (create, rename, update docstrings)
- `completed/` features are never touched by stub sync (only deprecation sync handles them)
- New stubs have NO default marker — the developer adds `@pytest.mark.unit` or `@pytest.mark.integration` when implementing
- The docstring includes EVERY step line in order, including `And` and `But` continuations
- Docstring format per step: `<Keyword>: <step text>` (e.g., `Given: user is logged in`, `And: user has admin role`)
- Test function bodies (code after the closing `"""` of the docstring) and parameter lists are NEVER modified
- Orphaned tests (no matching `@id` in any `.feature` file) receive `@pytest.mark.skip(reason="orphan: no matching @id in .feature files")`
- If a feature folder has no `.feature` files, skip silently

## Constraints
- Must never modify test function bodies or parameter lists
- Must handle the case where the test file does not yet exist (create it)
- Must handle the case where a test file exists but is missing some stubs (add only the missing ones)
- Function naming: `test_<feature_slug>_<id_hex>` where feature_slug is the folder name with hyphens replaced by underscores

## Questions
| ID | Question | Answer | Status |
|----|----------|--------|--------|
| Q1 | What is the stub body for a newly created test? | `raise NotImplementedError` only — no `# Given`, `# When`, or `# Then` section comments | ANSWERED |
| Q2 | Should the test file header (module docstring, imports) be preserved on update? | Yes — only the function name, decorators, and docstring are touched; file header is preserved | ANSWERED |

## Architecture

### Pre-mortem Summary

The current `syncer.py` has six structural defects that prevent satisfying the 18 acceptance criteria:
1. `_extract_steps` collapses all steps to three scalar strings — loses `And`/`But`/`*` keywords, DocStrings, DataTables, Background blocks, and Scenario Outline Examples tables.
2. `_stub_text` emits `@pytest.mark.unit` on every stub — violates `@id:d14d975f`.
3. `_stub_text` emits `# Given / # When / # Then` body comments — violates `@id:bba184c0`.
4. `_sync_one_feature` uses `folder_name` (kebab-case) for the test directory — violates `@id:edc964fc`.
5. `_sync_one_feature` skips if `test_file.exists()` — no update logic — violates all four `stub-update` criteria.
6. No orphan detection anywhere — violates both `orphan-marking` criteria.

The `_Example` dataclass (`id_hex, given, when, then, deprecated`) cannot represent ordered multi-step sequences with attachments. It must be replaced.

### Module Structure

All changes are confined to `pytest_beehave/syncer.py`. No new files are needed (YAGNI — the module boundary already exists and the public API `sync_stubs(features_dir, tests_dir)` is unchanged).

```
pytest_beehave/
  syncer.py   ← complete rewrite of internal functions; public API unchanged
```

### Data Structures

#### `_StepLine` (replaces the three scalar fields in `_Example`)

```python
@dataclass(frozen=True, slots=True)
class _StepLine:
    keyword: str          # literal keyword with trailing space stripped: "Given", "And", "But", "*", etc.
    text: str             # step text (raw template text for Scenario Outlines)
    doc_string: str | None   # content of attached DocString block, or None
    data_table: str | None   # pipe-formatted table rows, or None
```

`keyword` is taken directly from the Gherkin AST `step["keyword"].strip()`. This preserves `And`, `But`, `*` exactly as written — no mapping through `keywordType`.

`data_table` is rendered as a pipe-delimited string (e.g. `"| col1 | col2 |\n| a    | b    |"`) at parse time so the docstring builder is a pure string operation.

#### `_Example` (replaces the old dataclass)

```python
@dataclass(frozen=True, slots=True)
class _Example:
    id_hex: str
    steps: tuple[_StepLine, ...]          # ordered scenario steps (no background)
    background_sections: tuple[tuple[_StepLine, ...], ...]  # 0, 1, or 2 background groups
    outline_examples: str | None          # rendered Examples table for Scenario Outlines, or None
    deprecated: bool
```

`background_sections` is a tuple of step-tuples. The first element (if present) is the feature-level Background; the second (if present) is the Rule-level Background. This satisfies `@id:7f91cf3a` ("two Background: sections in order before the scenario steps").

`outline_examples` is a pre-rendered string of the Examples table (header + body rows in pipe format). Present only for `Scenario Outline` children. This satisfies `@id:9a4e199a`.

### Key Functions

#### `_render_step(step: _StepLine) -> str`

Renders one step line (and optional attachment) as docstring text:

```
Given: step text
```

If `doc_string` is present, appends it indented by 4 spaces below the step line.
If `data_table` is present, appends it indented by 4 spaces below the step line.
Satisfies `@id:c56883ce` and `@id:2fc458f8`.

#### `_build_docstring(example: _Example) -> str`

Assembles the full docstring body:
1. For each background section: emit `Background:` header, then render each step.
2. Render each scenario step.
3. If `outline_examples` is present, append it after the steps.

Returns the complete triple-quoted docstring string (without the outer `def` line).

#### `_stub_text(feature_slug: str, example: _Example) -> str`

Generates a complete new test function. Changes from current:
- **No `@pytest.mark.unit`** on new stubs (satisfies `@id:d14d975f`).
- Deprecated stubs get only `@pytest.mark.deprecated` (no `@pytest.mark.unit`).
- Body is `raise NotImplementedError` only — no section comments (satisfies `@id:bba184c0`).

#### `_parse_examples(feature_path: Path) -> list[_Example]`

Replaces the current implementation. New logic:
1. Parse the Gherkin AST.
2. Collect feature-level Background steps (if present) into `feature_bg`.
3. Walk `feature.children`:
   - If child is `background`: store as `feature_bg`.
   - If child is `scenario`: extract steps, check for Rule-level background (none at feature level), build `_Example`.
   - If child is `rule`: collect rule-level Background, then recurse into rule children for scenarios.
4. For each scenario, build `_StepLine` objects using `step["keyword"].strip()` (not `keywordType`).
5. For Scenario Outlines, render the `examples[0]` table into `outline_examples`.

#### `_collect_all_ids(features_dir: Path) -> frozenset[str]`

New function. Scans ALL stage directories (backlog, in-progress, completed) and returns the set of all `@id` hex values found in any `.feature` file. Used by orphan detection.

#### `_sync_one_feature(feature_path, folder_name, stage, tests_dir) -> str | None`

Rewritten. New logic:
- If `stage == "completed"`: return `None` immediately (satisfies `@id:38d864b9`, `@id:d89540f9`).
- Compute `feature_slug = _slugify(folder_name)` and `story_slug = _slugify(feature_path.stem)`.
- Compute `test_file = tests_dir / feature_slug / f"{story_slug}_test.py"` (uses `feature_slug` not `folder_name` — satisfies `@id:edc964fc`).
- If `test_file` does not exist: call `_create_stub_file(...)` (same as today).
- If `test_file` exists: call `_update_stub_file(...)` (new — satisfies stub-update criteria).

#### `_update_stub_file(feature_slug, story_slug, examples, test_file) -> str | None`

New function. Implements the update logic:

**Step 1 — Build known-id → `_Example` map** from the parsed `.feature` file.

**Step 2 — Parse existing test file** using a regex that captures each function block:
```
(decorators)(def test_<name>_<hex>() -> None:\n)(    """..."""\n)(body)
```
The regex captures: decorator block, full function name, 8-char hex, docstring, body.

**Step 3 — For each existing function block:**
- Extract the `id_hex` from the function name.
- Look up `id_hex` in the known-id map.
- If found: recompute the expected function name (`test_{feature_slug}_{id_hex}`) and expected docstring. If either differs, replace them in the source. Body is never touched (satisfies `@id:6bb59874`).
- If not found: leave unchanged (orphan handling is separate, file-level).

**Step 4 — For each `_Example` with no matching function in the file:** append a new stub at the end of the file.

**Step 5 — Write the updated source back** only if any change was made.

Returns an action string if changes were made, `None` otherwise.

#### `_sync_orphans(tests_dir: Path, all_ids: frozenset[str]) -> list[str]`

New function. Scans all `*_test.py` files under `tests_dir`. For each file:
- Find all `def test_\w+_([a-f0-9]{8})()` function definitions.
- For each: check if `hex` is in `all_ids`.
  - If not in `all_ids` and no orphan skip marker present: add `@pytest.mark.skip(reason="orphan: no matching @id in .feature files")` before the `def` line (satisfies `@id:9d7a0b34`).
  - If in `all_ids` and orphan skip marker present: remove the orphan skip marker (satisfies `@id:67192894`).
- Write the file back only if changed.

#### `sync_stubs(features_dir, tests_dir) -> list[str]` (public API — unchanged signature)

Updated orchestration:
1. Collect `all_ids = _collect_all_ids(features_dir)`.
2. For each stage in `(backlog, in-progress, completed)`: call `_sync_stage(...)` as today.
3. Call `_sync_orphans(tests_dir, all_ids)` and extend actions.
4. Return all actions.

### ADR-001: Keyword Preserved from AST `keyword` Field, Not `keywordType`

**Decision**: Use `step["keyword"].strip()` (the literal keyword string from the source file) rather than mapping `keywordType` to a canonical keyword.

**Reason**: `keywordType` collapses `And`, `But`, and `*` into `"Conjunction"` or `"Unknown"`, losing the literal keyword. The ACs require `And:`, `But:`, and `*:` to appear verbatim in the docstring (`@id:db596443`, `@id:17b01d7a`).

**Alternatives considered**: Mapping `keywordType` back to a keyword — rejected because it requires a language-specific lookup table and still cannot distinguish `And` from `But`.

### ADR-002: Regex-Based Test File Parsing (No AST)

**Decision**: Parse existing test files with a regex, not Python's `ast` module.

**Reason**: The update operation is a text substitution (replace docstring, rename function name). The regex captures the exact source text of each function block, enabling surgical replacement without disturbing surrounding whitespace, comments, or file structure. The `ast` module would require reconstructing source from the AST (lossy for comments and formatting).

**Alternatives considered**: `ast.parse` + `ast.unparse` — rejected because `unparse` does not preserve formatting and would corrupt the file header and body comments.

### ADR-003: `_collect_all_ids` Scans All Three Stages

**Decision**: Orphan detection scans `backlog/`, `in-progress/`, and `completed/` for known IDs.

**Reason**: A test function is orphaned only if its `@id` hex does not appear in ANY `.feature` file across all stages. Scanning only active stages would incorrectly mark tests for completed features as orphans.

**Alternatives considered**: Scanning only backlog + in-progress — rejected because it would mark all completed-feature tests as orphans.

### ADR-004: `_update_stub_file` Preserves File Header

**Decision**: The file header (module docstring + imports) is identified as everything before the first function block. It is never modified.

**Reason**: Q2 in discovery explicitly requires the file header to be preserved. The regex approach naturally preserves it because we only replace matched function blocks.

### ADR-005: Orphan Marker Is a Single Decorator Line

**Decision**: The orphan skip marker is exactly `@pytest.mark.skip(reason="orphan: no matching @id in .feature files")\n` — one line, added immediately before the `def` line (after any existing decorators).

**Reason**: The AC (`@id:9d7a0b34`) specifies the exact string. Placing it before `def` (after other decorators) is the standard pytest pattern and does not interfere with existing markers.

**Alternatives considered**: Inserting before all decorators — rejected because it would separate the skip marker from the function definition, making removal harder to target precisely.

### Build Changes (needs PO approval: no)

No new runtime dependencies. `gherkin-official` is already a dependency. All changes are internal to `pytest_beehave/syncer.py`.

### Contradiction Check Against All 18 Acceptance Criteria

| @id | AC Summary | Architecture Satisfies? | Notes |
|-----|-----------|------------------------|-------|
| `692972dd` | Correct function name `test_<feature_slug>_<id_hex>` | ✅ | `_stub_text` uses `feature_slug` |
| `d14d975f` | No default pytest marker on new stubs | ✅ | ADR-001; `_stub_text` emits no marker |
| `db596443` | `And:` / `But:` literal keywords in docstring | ✅ | ADR-001; `_StepLine.keyword` = literal |
| `17b01d7a` | `*:` for bullet steps | ✅ | ADR-001; `*` preserved from AST |
| `c56883ce` | DocString content indented below step line | ✅ | `_render_step` handles `doc_string` |
| `2fc458f8` | DataTable rows indented below step line | ✅ | `_render_step` handles `data_table` |
| `7f91cf3a` | Two `Background:` sections before scenario steps | ✅ | `_Example.background_sections` tuple |
| `9a4e199a` | Scenario Outline: raw template text + Examples table | ✅ | `_Example.outline_examples` |
| `777a9638` | Stub body ends with `raise NotImplementedError` | ✅ | `_stub_text` body |
| `bba184c0` | No `# Given / # When / # Then` comments in body | ✅ | `_stub_text` body is bare `raise` |
| `edc964fc` | Test directory uses underscore slug | ✅ | `test_file = tests_dir / feature_slug / ...` |
| `38d864b9` | No stubs created for completed features | ✅ | `_sync_one_feature` returns `None` for `completed` |
| `bdb8e233` | Docstring updated when step text changes | ✅ | `_update_stub_file` Step 3 |
| `6bb59874` | Test body not modified during docstring update | ✅ | ADR-002; regex captures body separately |
| `b6b9ab28` | Function renamed when feature slug changes | ✅ | `_update_stub_file` Step 3 |
| `d89540f9` | Completed feature stubs not updated | ✅ | `_sync_one_feature` returns `None` for `completed` |
| `9d7a0b34` | Orphan test receives skip marker | ✅ | `_sync_orphans` + ADR-005 |
| `67192894` | Orphan loses skip marker when matching Example added | ✅ | `_sync_orphans` removes marker when `hex` in `all_ids` |

No contradictions found.
