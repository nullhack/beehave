# Architecture: pytest-beehave

---

## 2026-04-18 — stub-creation: test file writing library

Decision: Use libcst for all test file writes.
Reason: Preserves formatting, comments, and existing function bodies; avoids string-template fragility.
Alternatives considered: `ast` module (cannot round-trip source with formatting preserved), string templates (fragile).
Feature: stub-creation

---

## 2026-04-18 — stub-creation: stub body

Decision: New stubs contain only `raise NotImplementedError` — no `# Given`, `# When`, `# Then` section comments.
Reason: Section comments are redundant given the docstring.
Alternatives considered: Adding section comments — rejected per AC Q1.
Feature: stub-creation

---

## 2026-04-18 — stub-creation: slug conventions

Decision: `FeatureSlug` replaces hyphens with underscores (for Python identifiers); `RuleSlug` uses underscores (for file names and Python identifiers).
Reason: Python function names cannot contain hyphens; file names can.
Alternatives considered: Both using underscores — rejected because file names with underscores diverge from the naming spec.
Feature: stub-creation

---

## 2026-04-18 — stub-creation: completed/ features excluded from stub sync

Decision: Stub creation is never invoked for features in `FeatureStage.COMPLETED`.
Reason: Matches AC `@id:38d864b9` and state machine.
Alternatives considered: Allowing stub creation for completed features — rejected per spec.
Feature: stub-creation

---

## 2026-04-18 — stub-updates: non-conforming handling creates conforming stub first

Decision: When a non-conforming stub is found, `sync_engine` first creates the conforming stub, then marks the original with `@pytest.mark.skip(reason="non-conforming: moved to <file>")`.
Reason: Ensures traceability is never lost — the conforming stub exists before the original is marked.
Alternatives considered: Delete the non-conforming stub — rejected because it loses the developer's implementation.
Feature: stub-updates

---

## 2026-04-18 — stub-updates: stub_reader uses libcst

Decision: `read_stubs_from_file` uses `libcst` to parse the test file and extract function names, decorators, and docstrings.
Reason: Consistent with stub_writer's use of libcst; avoids dual-library complexity.
Alternatives considered: `ast` module — rejected because it cannot extract decorator arguments reliably without round-trip capability.
Feature: stub-updates

---

## 2026-04-18 — stub-updates: stub-sync never touches @pytest.mark.slow

Decision: All stub_writer functions check the marker name before modifying; `slow` is never added or removed.
Reason: Matches marker ownership rules in discovery.md and AC `@id:c9a30d52`.
Alternatives considered: Allowing stub-sync to manage all markers — rejected per spec.
Feature: stub-updates

---

## 2026-04-18 — Cross-feature: remove class-based test structure

Decision: All test stubs are top-level functions. No `class Test<RuleSlug>` wrapping.
Reason: Class wrapping added indirection with no benefit; final implementation uses top-level functions throughout.
Alternatives considered: Keeping class-based layout for Rule blocks — rejected because it increases nesting without providing value.
Affected features: stub-creation, stub-updates

---

## 2026-04-18 — features-path-config: use stdlib tomllib

Decision: Use `tomllib` from the standard library (Python ≥ 3.11) for reading `pyproject.toml`.
Reason: No new runtime dependency needed; project already requires Python ≥ 3.13.
Alternatives considered: `tomli` (backport) — rejected because Python 3.13 is already required.
Feature: features-path-config

---

## 2026-04-18 — features-path-config: BeehaveConfig as a frozen dataclass

Decision: `@dataclass(frozen=True, slots=True)` with a single `features_path: Path` field.
Reason: Typed, immutable, and easy to extend with future config keys without changing callers.
Alternatives considered: Returning a raw `Path` — rejected because it cannot be extended without breaking callers.
Feature: features-path-config

---

## 2026-04-18 — features-path-config: read_config takes project_root as a parameter

Decision: Caller supplies the project root; `read_config` does not walk the filesystem to find it.
Reason: Keeps the function pure and testable without filesystem side effects; the plugin hook supplies the root.
Alternatives considered: Auto-detect by walking up from `cwd` — rejected because it couples the function to the process environment.
Feature: features-path-config

---

## 2026-04-18 — plugin-hook: use pytest_configure hook for pre-collection sync

Decision: Run stub sync inside `pytest_configure` so stubs exist before collection begins.
Reason: `pytest_configure` is called before collection; `pytest_sessionstart` is called after — using the latter would miss newly generated stubs in the same run.
Alternatives considered: `pytest_collection_start` — not a standard hook; `pytest_sessionstart` — runs too late.
Feature: plugin-hook

---

## 2026-04-18 — plugin-hook: inject filesystem and terminal writer as Protocol adapters

Decision: `plugin.py` instantiates `_RealFileSystem` and `_PytestTerminalWriter` and passes them to `run_sync` and `reporter` functions.
Reason: Keeps `sync_engine` and `reporter` testable without a live pytest session or real filesystem.
Alternatives considered: Direct use of `pathlib` and `config.get_terminal_writer()` inside sync_engine — rejected because it couples orchestration to pytest internals.
Feature: plugin-hook

---

## 2026-04-18 — plugin-hook: graceful skip when features directory is absent

Decision: `pytest_configure` checks `features_root.exists()` before calling `run_sync`; if absent, returns silently.
Reason: Matches AC `@id:d0f2866d` — pytest must complete without errors when the features directory does not exist.
Alternatives considered: Raising an error — rejected per AC.
Feature: plugin-hook

---

## 2026-04-18 — deprecation-sync: tag inheritance resolved at parse time

Decision: `parse_feature` resolves `@deprecated` inheritance (Feature → Rule → Example) and sets `ParsedExample.is_deprecated` as a flat bool.
Reason: Keeps sync_engine simple — it only reads `example.is_deprecated`; no inheritance logic scattered across modules.
Alternatives considered: Resolving inheritance in sync_engine — rejected because it duplicates logic and couples sync_engine to Gherkin tag semantics.
Feature: deprecation-sync

---

## 2026-04-18 — deprecation-sync: deprecation sync runs on completed/ features

Decision: `run_sync` calls deprecation sync for all three stages, including `completed/`.
Reason: Matches AC `@id:fc372f15` and discovery rule: "Deprecation sync is the ONLY operation performed on completed/ feature test files."
Alternatives considered: Skipping `completed/` for deprecation sync — rejected per spec.
Feature: deprecation-sync

---

## 2026-04-18 — deprecation-sync: no duplicate @pytest.mark.deprecated markers

Decision: `toggle_deprecated_marker` reads existing markers via `stub_reader` before writing; skips if already in correct state.
Reason: Matches constraint "Must not add duplicate @pytest.mark.deprecated markers".
Alternatives considered: Always removing then re-adding — rejected because it causes unnecessary file writes.
Feature: deprecation-sync

---

## 2026-04-18 — auto-id-generation: detect read-only by checking file writability

Decision: Use `os.access(path, os.W_OK)` via `FileSystemProtocol.is_writable` to determine if write-back is possible.
Reason: More reliable across different CI systems than checking `CI` env var; matches AC Q2 answer.
Alternatives considered: Checking `os.environ.get("CI")` — rejected per AC Q2.
Feature: auto-id-generation

---

## 2026-04-18 — auto-id-generation: ID uniqueness is within-file only

Decision: `generate_unique_id` takes `existing_ids: set[ExampleId]` scanned from the current file only.
Reason: Matches AC Q1 answer; cross-file collision probability with 8-char hex is negligible.
Alternatives considered: Global uniqueness across all feature files — rejected per AC Q1.
Feature: auto-id-generation

---

## 2026-04-18 — auto-id-generation: write @id tag on the line immediately before the Example keyword

Decision: Insert the `@id:<hex>` tag line immediately before the `Example:` keyword line.
Reason: Matches the Gherkin tag convention and AC requirement.
Alternatives considered: Appending to existing tag lines — rejected because it may break gherkin-official parsing.
Feature: auto-id-generation

---

## 2026-04-18 — features-dir-bootstrap: bootstrap is a pure function of the filesystem state

Decision: `bootstrap_features_directory` takes only `features_root: Path` and performs all filesystem operations directly via `pathlib`.
Reason: Bootstrap operations (mkdir, rename) are idempotent and low-risk; no Protocol abstraction needed at this scale.
Alternatives considered: Injecting a filesystem Protocol — rejected because bootstrap is simple enough that the added indirection is YAGNI.
Feature: features-dir-bootstrap

---

## 2026-04-18 — features-dir-bootstrap: BootstrapResult.is_noop drives terminal output

Decision: `report_bootstrap` produces no output when `result.is_noop` is True.
Reason: Matches AC `@id:5e6f9b17` — no output when structure is already correct.
Alternatives considered: Always printing a "bootstrap OK" message — rejected per AC.
Feature: features-dir-bootstrap

---

## 2026-04-18 — features-dir-bootstrap: name collision leaves root-level file in place with a warning

Decision: When a root-level `.feature` file shares a name with an existing `backlog/` file, `bootstrap_features_directory` records the filename in `collision_warnings` and does not move the file.
Reason: Matches AC `@id:7f2a0d51` and `@id:8c3b1e96`; prevents data loss.
Alternatives considered: Overwriting the backlog file — rejected because it loses the existing backlog file.
Feature: features-dir-bootstrap

---

## 2026-04-19 — stub-creation, stub-updates: drop libcst in favour of direct string manipulation

Decision: `stub_writer` and `stub_reader` use direct string parsing/formatting rather than `libcst`.
Reason: The implementation does not need to round-trip arbitrary Python source with full formatting preservation. Direct string manipulation is simpler, has zero additional dependencies, and is sufficient for the structured output format (top-level functions with a docstring and `raise NotImplementedError`). `libcst` was never added as a runtime dependency.
Supersedes: "2026-04-18 — stub-creation: test file writing library" and "2026-04-18 — stub-updates: stub_reader uses libcst"
Feature: stub-creation, stub-updates
