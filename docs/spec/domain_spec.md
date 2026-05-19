# Domain Specification: beehave

## Context Map

### Context Relationships

| Upstream Context | Downstream Context | Relationship Pattern | Translation Notes |
|-----------------|-------------------|---------------------|-------------------|
| Feature Parsing | Consistency Checking | CONFORMIST | ScenarioInfo consumed as-is |
| Feature Parsing | Code Generation | CONFORMIST | ScenarioInfo consumed as-is |
| Feature Parsing | Status Reporting | CONFORMIST | ScenarioInfo consumed as-is |
| Test Discovery | Consistency Checking | CONFORMIST | TestInfo consumed as-is |
| Test Discovery | Code Generation | CONFORMIST | TestInfo consumed as-is |
| Test Discovery | Status Reporting | CONFORMIST | TestInfo consumed as-is |
| Consistency Checking | Status Reporting | CONFORMIST | Violation tuples consumed as-is |
| Configuration | Feature Parsing | OHS | Config provides directories, background_check flags |
| Configuration | Test Discovery | OHS | Config provides directory paths only |
| Configuration | Code Generation | OHS | Config provides default_strategy mapping |
| Configuration | Status Reporting | OHS | Config provides directory paths |
| CLI | Feature Parsing | PL | CLI dispatches to parse_feature via cmd_* handlers |
| CLI | Test Discovery | PL | CLI dispatches via cmd_* handlers |
| CLI | Consistency Checking | PL | CLI dispatches via cmd_* handlers |
| CLI | Status Reporting | PL | CLI dispatches via cmd_status handler |

### Context Map Diagram

```mermaid
graph TB
    CLI[CLI Interface] -->|PL| FeatureParsing[Feature Parsing]
    CLI -->|PL| TestDiscovery[Test Discovery]
    CLI -->|PL| ConsistencyChecking[Consistency Checking]
    CLI -->|PL| StatusReporting[Status Reporting]
    Config[Configuration] -->|OHS| FeatureParsing
    Config -->|OHS| TestDiscovery
    Config -->|OHS| CodeGen[Code Generation]
    Config -->|OHS| StatusReporting
    FeatureParsing -->|CONFORMIST| ConsistencyChecking
    FeatureParsing -->|CONFORMIST| CodeGen
    FeatureParsing -->|CONFORMIST| StatusReporting
    TestDiscovery -->|CONFORMIST| ConsistencyChecking
    TestDiscovery -->|CONFORMIST| CodeGen
    TestDiscovery -->|CONFORMIST| StatusReporting
    ConsistencyChecking -->|CONFORMIST| StatusReporting
```

### Anti-Corruption Layers

| ACL | Protects Context | From Context | ADR Reference |
|-----|-----------------|--------------|---------------|
| — | — | — | No external systems |

---

## Feature Parsing

### Context

Parses Gherkin `.feature` files into structured domain objects. This context owns the canonical representation of a feature: its title, path, background steps, rules, scenarios, placeholders, literals, and examples tables. All downstream contexts consume ScenarioInfo without modification.

### Entities

| Name | Type | Purpose | Aggregate Root? |
|------|------|---------|-----------------|
| ScenarioInfo | Entity | Represents a parsed Gherkin scenario with all extracted metadata (steps, placeholders, literals, examples table) | Yes |
| ParsedStep | Value Object | A single Given/When/Then step with extracted keywords, placeholders, and literals | — |
| Placeholder | Value Object | A `<name>` token extracted from step text | — |
| Literal | Value Object | A numeric or quoted-string token extracted from step text | — |
| ExamplesTable | Value Object | The Examples data table from a Scenario Outline | — |

### Relationships

| Subject | Relation | Object | Cardinality | Notes |
|---------|----------|--------|-------------|-------|
| ScenarioInfo | contains | ParsedStep | 1:N | Merged feature background + rule background + scenario steps |
| ScenarioInfo | contains | Placeholder | 1:N | Deduplicated across all merged steps |
| ScenarioInfo | contains | Literal | 1:N | From scenario steps always; from backgrounds only if config enables |
| ScenarioInfo | references | ExamplesTable | 0:1 | Only for Scenario Outlines |
| Feature | contains | ScenarioInfo | 1:N | Feature file aggregates all scenarios |

### Aggregate Boundaries

| Aggregate | Root Entity | Why Grouped | See |
|-----------|-------------|-------------|-----|
| Feature | ScenarioInfo | Feature file is the consistency unit — parsing, generation, checking, and status all operate per-feature | ### Invariants |

### Data Shapes

#### ScenarioInfo

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| title | str | Yes | Non-empty, letters/digits/spaces only |
| function_name | str | Yes | Derived: `test_` + title lowercased with underscores |
| steps | tuple[ParsedStep] | Yes | Merged bg + rule bg + scenario steps |
| placeholders | tuple[Placeholder] | Yes | Deduplicated |
| literals | tuple[Literal] | Yes | Not deduplicated |
| examples | ExamplesTable \| None | No | Present only for Scenario Outlines |
| is_outline | bool | Yes | True if Scenario Outline |
| feature_title | str | Yes | Feature-level title |
| feature_path | str | Yes | Slug derived from feature title |
| rule_path | str | Yes | "default_test" or "<rule_slug>_test" |
| line | int | Yes | Line number in .feature file |

#### TestInfo

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| function_name | str | Yes | Must match ScenarioInfo.function_name for mapping |
| given_kwargs | tuple[str] | Yes | Parameters from @given() decorator |
| example_rows | tuple[dict[str,object]] | Yes | Row dicts from @example() decorators |
| body_name_nodes | tuple[str] | Yes | All ast.Name identifiers in body (sorted) |
| body_constant_nodes | tuple[object] | Yes | All ast.Constant values in body (sorted) |
| is_stub | bool | Yes | True if body is only `pass` or `...` |
| line | int | Yes | Line number in test file |

#### Violation

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| path | str | Yes | File path where violation occurred |
| line | int | Yes | Line number (0 = unknown) |
| error_type | str | Yes | One of: unmapped-scenario, unmapped-test, missing-placeholder, missing-literal, example-mismatch, misplaced-test |
| message | str | Yes | Human-readable description |
| is_warning | bool | Yes | Only misplaced-test is a warning |

### Integration Points

#### Technology Requirements

| Context | Requirement | Verification |
|---------|-------------|-------------|
| Feature Parsing | gherkin-official library for AST parsing | grep import gherkin_official |
| Feature Parsing | Regular expressions for token extraction | grep re.compile |
| Feature Parsing | Python keyword/builtin validation | grep keyword.iskeyword |

#### Feature Parsing -> Consistency Checking

- Purpose: Provide parsed scenarios for violation detection
- Trigger: CLI invokes check command
- Mechanism: Direct function call (parse_feature returns dict[str, ScenarioInfo])
- Pattern: CONFORMIST
- Payload: {function_name: ScenarioInfo}
- Response: None (Consistency Checking consumes and produces Violations independently)
- Error handling: GherkinError raised on parse failure, caught by caller
- Ownership: Feature Parsing context

#### Feature Parsing -> Status Reporting

- Purpose: Provide parsed scenarios for stage computation
- Trigger: CLI invokes status command
- Mechanism: Direct function call (parse_feature returns dict[str, ScenarioInfo])
- Pattern: CONFORMIST
- Payload: {function_name: ScenarioInfo}
- Response: None
- Error handling: GherkinError caught, feature marked as broken stage
- Ownership: Feature Parsing context

### External Contracts

#### Contract: parse_feature(feature_path, config, seen_function_names=None) -> dict[str, ScenarioInfo]

- **Actor**: CLI or downstream context (Consistency Checking, Code Generation, Status Reporting)
- **Trigger**: Feature needs to be parsed from disk
- **Input**: {feature_path: Path, config: Config, seen_function_names: set[str] | None}
- **Output**: {function_name: ScenarioInfo} dict keyed by derived test function name
- **Errors**:
  - Gherkin syntax error -> GherkinError
  - Empty feature file -> GherkinError ("No feature found")
  - Invalid feature title -> GherkinError
  - Duplicate function name (if seen_function_names provided) -> GherkinError
  - Background with placeholders -> GherkinError
  - Invalid scenario title -> GherkinError
- **Side Effects**: Reads .feature file from disk
- **Preconditions**: Feature file exists at given path, is valid Gherkin

### State Machines

Not applicable — Feature Parsing has no internal state.

### Error Handling

| Scenario | Response |
|----------|----------|
| Invalid Gherkin syntax | GherkinError raised with line number and message |
| Feature with no scenarios or rules | Returns empty dict `{}` |
| Rule with no scenarios | Rule is present in Gherkin AST but produces no ScenarioInfo entries |

### Invariants

- Every scenario produces exactly one ScenarioInfo
- Function names must be valid Python identifiers
- Function names must not be Python keywords or builtins
- Feature title derivation is deterministic (title slug = lowercase, words joined by underscore)
- Background steps are merged transparently into every scenario's step list

---

## Test Discovery

### Context

Discovers and analyzes Python test files via AST parsing. Extracts test function metadata (decorator arguments, body AST nodes, stub status) to enable consistency checking and code generation. Owns the canonical representation of a test function's structure.

### Entities

| Name | Type | Purpose | Aggregate Root? |
|------|------|---------|-----------------|
| TestInfo | Entity | Represents a discovered test function with all extracted metadata | Yes |

### Relationships

| Subject | Relation | Object | Cardinality | Notes |
|---------|----------|--------|-------------|-------|
| TestInfo | contains | given_kwargs | 1:N | From @given() decorator |
| TestInfo | contains | example_rows | 0:N | From @example() decorators |
| TestInfo | contains | body_name_nodes | 0:N | ast.Name ids in function body |
| TestInfo | contains | body_constant_nodes | 0:N | ast.Constant values in function body |
| TestFile | contains | TestInfo | 1:N | One file can contain multiple test functions |

### Aggregate Boundaries

| Aggregate | Root Entity | Why Grouped | See |
|-----------|-------------|-------------|-----|
| TestFile | TestInfo | Test file is the unit of discovery — all test functions in a file are discovered together | ### Invariants |

### Integration Points

#### Technology Requirements

| Context | Requirement | Verification |
|---------|-------------|-------------|
| Test Discovery | Python AST module for parsing | grep import ast |
| Test Discovery | Hypothesis decorator introspection | grep @given |

#### Test Discovery -> Consistency Checking

- Purpose: Provide discovered test functions for violation detection
- Trigger: CLI invokes check command
- Mechanism: Direct function call (discover_tests returns dict[str, TestInfo])
- Pattern: CONFORMIST
- Payload: {function_name: TestInfo}
- Response: None
- Error handling: SyntaxError caught, file treated as containing zero tests
- Ownership: Test Discovery context

#### Test Discovery -> Status Reporting

- Purpose: Provide discovered test functions for stage computation
- Trigger: CLI invokes status command
- Mechanism: Direct function call (discover_tests returns dict[str, TestInfo])
- Pattern: CONFORMIST
- Payload: {function_name: TestInfo}
- Response: None
- Error handling: SyntaxError caught, file treated as empty
- Ownership: Test Discovery context

### External Contracts

#### Contract: discover_tests(test_file: Path) -> dict[str, TestInfo]

- **Actor**: CLI or downstream context
- **Trigger**: Test file needs analysis
- **Input**: {test_file: Path}
- **Output**: {function_name: TestInfo} dict keyed by function name
- **Errors**:
  - Python syntax error -> returns empty dict (file treated as empty)
  - File not found -> FileNotFoundError (unhandled)
- **Side Effects**: Reads test file from disk
- **Preconditions**: Test file exists and is valid Python

#### Contract: discover_tests_dir_with_paths(tests_dir: Path) -> dict[str, tuple[TestInfo, Path]]

- **Actor**: Consistency Checking (check_all)
- **Trigger**: Need all test functions across all features for cross-feature mapping
- **Input**: {tests_dir: Path}
- **Output**: {function_name: (TestInfo, file_path)} dict across all *_test.py files
- **Side Effects**: Recursively discovers all *_test.py files
- **Preconditions**: tests_dir exists

### State Machines

Not applicable — Test Discovery is stateless.

### Error Handling

| Scenario | Response |
|----------|----------|
| Test file with Python syntax error | Returns empty dict; all scenarios unmapped |
| Empty test file (0 bytes) | discover_tests returns {} |
| Test file with only imports, no functions | discover_tests returns {} |

### Invariants

- Function body is a stub if and only if it contains exactly one statement that is `pass` or `...`
- Leading docstring is excluded from body node analysis
- Stub detection is exact: a body with docstring + pass (2 statements) is NOT a stub

---

## Consistency Checking

### Context

Verifies that parsed feature scenarios and discovered test functions are consistent. Produces violations when scenarios are unmapped, test functions are orphaned, placeholders or literals are missing from test bodies, or example rows don't match. Supports both single-feature (`check_single`) and all-features (`check_all`) modes.

### Entities

| Name | Type | Purpose | Aggregate Root? |
|------|------|---------|-----------------|
| Violation | Value Object | A single consistency issue (path, line, error_type, message, is_warning) | — |

### Relationships

Not applicable — Violation is a standalone value object.

### Aggregate Boundaries

Not applicable — Checking is stateless.

### Integration Points

#### Technology Requirements

| Context | Requirement | Verification |
|---------|-------------|-------------|
| Consistency Checking | Feature parsing | grep from beehave.gherkin import |
| Consistency Checking | Test discovery | grep from beehave.discover import |

#### Consistency Checking -> Status Reporting

- Purpose: Provide per-scenario violations for status computation
- Trigger: Status command computes stage for each scenario
- Mechanism: Direct call to check_pair(si, ti, test_path, feature_rel)
- Pattern: CONFORMIST
- Payload: (ScenarioInfo, TestInfo, Path, Path) -> list[Violation]
- Response: List of violations (empty if all checks pass), skips checks if test is stub
- Ownership: Consistency Checking context

### External Contracts

#### Contract: check_pair(si, ti, test_path, feature_path) -> list[Violation]

- **Actor**: Status Reporting, Consistency Checking
- **Trigger**: A scenario-test pair needs validation
- **Input**: {si: ScenarioInfo, ti: TestInfo | None, test_path: Path, feature_path: Path}
- **Output**: list of Violation objects
- **Errors**:
  - ti is None -> unmapped-scenario violation
  - Placeholder not in ti.body_name_nodes -> missing-placeholder violation
  - Literal not in ti.body_constant_nodes -> missing-literal violation
  - Examples table row count != @example() decorator count -> example-mismatch violation
- **Preconditions**: si and ti are properly parsed

#### Contract: check_single(feature_path, config) -> list[Violation]

- **Actor**: CLI (beehave check <feature>)
- **Trigger**: Single feature check
- **Input**: {feature_path: Path, config: Config}
- **Output**: All violations for the feature
- **Side Effects**: Reads .feature file, discovers matching test files

#### Contract: check_all(config) -> list[Violation]

- **Actor**: CLI (beehave check)
- **Trigger**: Full project check
- **Input**: {config: Config}
- **Output**: All violations across all features
- **Side Effects**: Reads all .feature files, discovers all *_test.py files

### Error Handling

| Scenario | Response |
|----------|----------|
| Stub test with missing placeholder | No violation (stubs skip all checks) |
| Stub test with missing literal | No violation |
| Stub test with example mismatch | No violation |
| Misplaced test (wrong directory) | Warning only, does not affect exit code |

### Invariants

- Stubs are exempt from all body-based violation checks
- Misplaced-test is the ONLY warning-level violation; all others are errors
- Exit code 1 when any non-warning violation exists
- Exit code 0 when only warnings exist

---

## Code Generation

### Context

Generates Hypothesis test stubs from parsed feature files. Creates test directories, __init__.py files, and *_test.py files with @given() decorators for placeholders and @example() decorators for Scenario Outline rows. Preserves existing non-stub test functions during regeneration.

### Entities

Not applicable — Code Generation produces files, not domain objects.

### Integration Points

#### Technology Requirements

| Context | Requirement | Verification |
|---------|-------------|-------------|
| Code Generation | Feature parsing | grep from beehave.gherkin import |
| Code Generation | Test discovery | grep from beehave.discover import |
| Code Generation | Hypothesis imports in generated code | grep import hypothesis |
| Code Generation | Zero beehave imports in generated code | grep -v import beehave in generated files |

### External Contracts

#### Contract: generate_stubs(feature_path, config) -> None

- **Actor**: CLI (beehave generate <feature>)
- **Trigger**: Developer needs test stubs for a feature
- **Input**: {feature_path: str, config: Config}
- **Output**: Creates directories and test files on disk
- **Side Effects**: Creates tests/features/<feature_slug>/ directory, __init__.py, and *_test.py files
- **Preconditions**: Feature file is valid Gherkin

### Error Handling

| Scenario | Response |
|----------|----------|
| Feature with zero scenarios | Returns without creating anything |
| Existing non-stub test function | Preserved, new stub appended for new scenarios only |

### Invariants

- Generated code imports only from hypothesis — never from beehave
- Stub body is always `...` (Ellipsis)
- Strategy resolution order: module-level variable > Examples table type > default config

---

## Status Reporting

### Context

Computes and displays the development stage of each feature by synthesizing data from Feature Parsing, Test Discovery, and Consistency Checking. Derives stages entirely from disk state — no stored state, no caching. The command is a pure presentation layer with no new parsing or heuristics.

### Entities

| Name | Type | Purpose | Aggregate Root? |
|------|------|---------|-----------------|
| ScenarioStatus | Value Object | Computed status of a single scenario (no test / no body / N errors / ok) | — |
| FeatureStatus | Value Object | Computed status of a feature across all its scenarios | — |
| StatusReport | Value Object | Aggregate report of all features, orphaned directories, and collisions | — |

### Relationships

| Subject | Relation | Object | Cardinality | Notes |
|---------|----------|--------|-------------|-------|
| FeatureStatus | contains | ScenarioStatus | 1:N | One per scenario in the feature |
| StatusReport | contains | FeatureStatus | 1:N | One per .feature file |
| StatusReport | contains | OrphanedDir | 0:N | Test dirs with no matching .feature |
| StatusReport | contains | Collision | 0:N | Cross-feature function name collisions |

### Aggregate Boundaries

| Aggregate | Root Entity | Why Grouped | See |
|-----------|-------------|-------------|-----|
| StatusReport | StatusReport | Single output unit — computed in one pass, formatted once | ### Invariants |

### Data Shapes

#### ScenarioStatus

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| title | str | Yes | Scenario title |
| function_name | str | Yes | Derived test function name |
| status | str | Yes | "no test" / "no body" / "{N} errors" / "ok" |
| is_stub | bool | Yes | True if test body is pass/... |
| is_outline | bool | Yes | True if Scenario Outline |
| line | int | Yes | Line number |
| violations | tuple[Violation] | Yes | Violations from check_pair (empty for ok/stub/no test) |

#### FeatureStatus

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| path | str | Yes | Feature slug |
| title | str | Yes | Feature title from Gherkin |
| stage | str | Yes | "broken" / "no scenarios" / "needs scenarios" / "needs tests" / "needs bodies" / "needs fixes" / "ok" |
| scenarios_total | int | Yes | Total scenario count |
| scenarios_ok | int | Yes | Passing scenario count |
| scenarios_errors | int | Yes | Failing scenario count |
| scenarios_no_body | int | Yes | Stub scenario count |
| scenarios_no_test | int | Yes | Unmapped scenario count |
| violations_error_count | int | Yes | Total non-warning violations |
| violations_warning_count | int | Yes | Total warning violations |
| parse_error_message | str \| None | No | Set when stage == "broken" |
| scenarios | tuple[ScenarioStatus] | Yes | Per-scenario detail |

### Integration Points

#### Technology Requirements

| Context | Requirement | Verification |
|---------|-------------|-------------|
| Status Reporting | Feature parsing | grep from beehave.gherkin import |
| Status Reporting | Test discovery | grep from beehave.discover import |
| Status Reporting | Consistency checking | grep from beehave.check import check_pair |
| Status Reporting | CLI integration | grep status in cli.py |

### External Contracts

#### Contract: beehave status [feature] [options]

- **Actor**: Developer, CI pipeline
- **Trigger**: CLI invocation
- **Input**: Optional feature path slug, optional flags (--json, --stage, --no-color, etc.)
- **Output**: 
  - Default: Tree-based hierarchy showing feature/rule/scenario status
  - JSON: Machine-readable status report with full hierarchy and counts
- **Exit codes**:
  - 0: All features ok (or empty, or no features)
  - 1: At least one feature not ok
  - 2: Fatal error
- **Side Effects**: Reads .feature files and test files from disk. No writes.
- **Preconditions**: Project has a valid Config (features_dir, tests_dir)

### Stage Decision Tree

| Priority | Condition | Stage |
|----------|-----------|-------|
| 1 | parse_feature() raises GherkinError | broken |
| 2 | parse_feature() returns {} (0 scenarios) | no scenarios |
| 3 | Feature has Rules but every Rule has zero Scenarios | needs scenarios |
| 4 | Any scenario has no matching test function (unmapped) | needs tests |
| 5 | All scenarios mapped AND any matched test is a stub | needs bodies |
| 6 | All scenarios mapped, all non-stub, AND any check_pair() violation | needs fixes |
| 7 | All scenarios mapped, all non-stub, zero violations | ok |

### Scenario Status Decision Tree

| Priority | Condition | Status |
|----------|-----------|--------|
| 1 | No matching TestInfo found | no test |
| 2 | TestInfo.is_stub is True | no body |
| 3 | check_pair() returns non-empty violations | {N} errors |
| 4 | check_pair() returns empty violations | ok |

### Output Format (Human-Readable)

Tree-based hierarchy with status labels on the left in a fixed-width column:

```
needs fixes     hive_activity (Hive Activity)
  ok            ├── honey production from nectar           (3 ex)
  2 errors      ├── Hive defense
  2 errors      │   ├── guard bee inspects visitor         scent, floral
  no body       │   └── guard bee inspects visitor2
  ok            └── Foraging
  ok                └── forager returns with nectar

  ok            comb_construction (Comb Construction)
```

- `ok` features collapse to one line
- Rule aggregate shows worst child status with counts
- Scenario Outlines show example count: `(N ex)`
- Failing scenarios show violation codes inline

### Output Format (JSON)

```json
{
  "features": [{
    "path": "hive_activity",
    "title": "Hive Activity",
    "stage": "needs fixes",
    "scenarios_total": 4,
    "scenarios_ok": 2,
    "scenarios_errors": 1,
    "scenarios_no_body": 1,
    "scenarios_no_test": 0,
    "scenarios": [{
      "title": "guard bee inspects visitor",
      "function_name": "test_guard_bee_inspects_visitor",
      "status": "2 errors",
      "is_stub": false,
      "is_outline": false,
      "line": 23,
      "violations": [
        {"error_type": "missing-placeholder", "message": "literal 'scent' not found", "line": 23},
        {"error_type": "missing-literal", "message": "literal 'floral' not found", "line": 23}
      ]
    }]
  }],
  "orphaned_directories": [],
  "collisions": [],
  "summary": {
    "total_features": 2,
    "broken": 0,
    "no_scenarios": 0,
    "needs_scenarios": 0,
    "needs_tests": 0,
    "needs_bodies": 0,
    "needs_fixes": 1,
    "ok": 1
  }
}
```

### Error Handling

| Scenario | Response |
|----------|----------|
| Parse error in feature | Stage = "broken", error message shown |
| Feature with no scenarios or rules | Stage = "no scenarios" |
| Feature with Rules but no Scenarios | Stage = "needs scenarios" |
| Rule aggregate: mixed status | Shows worst status with counts (e.g., "1 error, 1 no body") |
| Orphaned test directory (no .feature) | Reported in orphaned_directories if --include-orphaned |

### Invariants

- Stage is always computed from disk state, never stored
- Parse errors are first-class stages, not side-channel stderr
- Warnings (misplaced tests, name collisions) do not affect stage
- Exit codes mirror beehave check: 0 = clean, 1 = work to do, 2 = fatal

---

## CLI Interface

### Context

Provides the user-facing command-line interface for all beehave operations. Uses argparse for subcommand dispatch. Owns the mapping from CLI flags to context function calls.

### Entities

Not applicable — CLI is a dispatch layer.

### Integration Points

#### Technology Requirements

| Context | Requirement | Verification |
|---------|-------------|-------------|
| CLI Interface | argparse for subcommand parsing | grep import argparse |
| CLI Interface | Entry point: beehave = "beehave.cli:main" | grep beehave pyproject.toml |

### External Contracts

#### Commands

| Command | Args | Context Called |
|---------|------|---------------|
| generate | feature (required) | Code Generation |
| check | feature (optional) | Consistency Checking |
| clean | feature (required), --force | Cleanup |
| list | --verbose | Status Reporting (existing list command) |
| status | feature (optional), --json, --stage, --no-color | Status Reporting (new) |

#### Exit Code Contract

- Exit 0: No errors (or only warnings)
- Exit 1: Non-warning violations exist (check) or non-ok features exist (status)
- Exit 2: Fatal error (config missing, disk I/O failure)

### State Machines

Not applicable.

### Error Handling

| Scenario | Response |
|----------|----------|
| Config file missing | Uses defaults, no error |
| Invalid subcommand | argparse shows help, exits 2 |

### Invariants

- All commands write to stdout, errors to stderr (except status: parse errors are stdout stages)
- Exit code semantics are consistent across all commands

---

## Configuration

### Context

Provides project configuration loaded from pyproject.toml under `[tool.beehave]`. Defines directory paths, default strategy, and background check flags. All contexts consume Config as an immutable frozen dataclass.

### Entities

| Name | Type | Purpose | Aggregate Root? |
|------|------|---------|-----------------|
| Config | Value Object | Immutable configuration with directory paths, strategy, and boolean flags | — |

### Data Shapes

#### Config

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| features_dir | str | Yes | Default: "docs/features" |
| tests_dir | str | Yes | Default: "tests/features" |
| default_strategy | str | Yes | One of: text, integers, floats, booleans |
| background_check_numeric | bool | Yes | Default: True |
| background_check_string | bool | Yes | Default: True |

### Integration Points

#### Technology Requirements

| Context | Requirement | Verification |
|---------|-------------|-------------|
| Configuration | TOML parsing via tomllib | grep import tomllib |
| Configuration | Strategy map for Hypothesis expressions | grep _STRATEGY_MAP |

### External Contracts

#### Contract: load_config(project_root=None) -> Config

- **Actor**: CLI, all contexts
- **Trigger**: Command execution begins
- **Input**: {project_root: Path | None}
- **Output**: Config with values from pyproject.toml or defaults
- **Side Effects**: Reads pyproject.toml
- **Preconditions**: Running from within a beehave project tree

### Error Handling

| Scenario | Response |
|----------|----------|
| pyproject.toml missing | Returns Config with all defaults |
| Invalid default_strategy value | ValueError |

### Invariants

- Config is frozen — never mutated after creation
- Strategy expressions are stable mappings (text -> st.text(), integers -> st.integers(), etc.)
