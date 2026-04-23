# System Overview: beehave

> Current-state description of the production system.
> Rewritten by the system-architect at Step 2 for each feature cycle.
> Contains only completed features — nothing from backlog or in-progress.

---

## Summary

beehave is a BDD living-documentation sync tool that keeps test stubs in sync with Gherkin `.feature` files. It reads `.feature` files as the source of truth, generates framework-specific test stubs, and updates existing stubs when features change — without ever modifying test bodies. The system is a single Python package (`pytest_beehave`) with CLI and Python API surfaces, using `fire` for command dispatch and `gherkin-official` for parsing.

---

## Context

### Actors

| Actor | Description |
|-------|-------------|
| `Developer` | Python engineer using beehave to manage BDD test stubs |
| `CI Pipeline` | Automated system running `beehave nest --check` or `beehave status` for verification |

### Systems

| System | Kind | Description |
|--------|------|-------------|
| `beehave` | Internal | BDD living-documentation sync tool with CLI and Python API |
| `pyproject.toml` | External | Project configuration file; beehave reads and writes `[tool.beehave]` section |
| `Filesystem` | External | Directory structure managed by `beehave nest`; feature files and test stubs on disk |

### Interactions

| Interaction | Behaviour | Technology |
|-------------|-----------|------------|
| Developer → beehave CLI | Runs `beehave nest`, `beehave sync`, `beehave status`, etc. | CLI / fire |
| Developer → beehave Python API | Imports `from pytest_beehave import ...` | Python import |
| CI Pipeline → beehave CLI | Runs `beehave nest --check` or `beehave status --json` | CLI / subprocess |
| beehave → pyproject.toml | Reads `[tool.beehave]` config; injects section if absent | tomllib (stdlib) |
| beehave → Filesystem | Creates directories, writes stubs, reads feature files | pathlib (stdlib) |

---

## Container

### Boundary: beehave

| Container | Technology | Responsibility |
|-----------|------------|----------------|
| CLI Entrypoint | Python / fire | Dispatches subcommands (nest, sync, status, hatch, version) |
| Config Reader | Python / tomllib | Reads and writes `[tool.beehave]` from pyproject.toml |
| Nest Command | Python / pathlib | Bootstraps canonical directory structure and injects config |
| Feature Parser | Python / gherkin-official | Parses `.feature` files into domain models |
| ID Generator | Python / secrets | Assigns unique 8-char hex IDs to untagged Examples |
| Stub Writer | Python / string templates | Generates framework-specific test stub files |
| Sync Engine | Python | Orchestrates stub creation, update, and cleanup |
| Hatch Command | Python / secrets | Generates bee-themed demo `.feature` files |

### Interactions

| Interaction | Behaviour |
|-------------|-----------|
| Developer → CLI Entrypoint | Invokes via `beehave <command>` |
| CLI Entrypoint → Nest Command | Dispatches `beehave nest` with flags |
| CLI Entrypoint → Hatch Command | Dispatches `beehave hatch` with flags |
| Nest Command → Config Reader | Reads and injects `[tool.beehave]` section |
| Nest Command → Filesystem | Creates directories and `.gitkeep` files |
| Sync Engine → Feature Parser | Parses `.feature` files for sync |
| Sync Engine → Stub Writer | Writes generated stubs to disk |
| Sync Engine → ID Generator | Assigns IDs to untagged Examples |

---

## Structure

| Module | Responsibility |
|--------|----------------|
| `pytest_beehave/__main__.py` | CLI entrypoint: BeehaveCLI class with subcommand methods |
| `pytest_beehave/__init__.py` | Package marker; no public API |
| `pytest_beehave/config.py` | Reads and writes `[tool.beehave]` from pyproject.toml |
| `pytest_beehave/nest.py` | Nest command: bootstraps directory structure, injects config |
| `pytest_beehave/bootstrap.py` | Directory structure migration: subfolder creation, loose file migration |
| `pytest_beehave/models.py` | Shared value objects: FeatureStage, ExampleId, FeatureSlug, RuleSlug |
| `pytest_beehave/feature_parser.py` | Parses `.feature` files into domain objects |
| `pytest_beehave/id_generator.py` | Generates unique 8-char hex IDs for Examples |
| `pytest_beehave/stub_writer.py` | Writes test stub files to disk |
| `pytest_beehave/stub_reader.py` | Reads existing test stubs for sync comparison |
| `pytest_beehave/sync_engine.py` | Orchestrates stub creation, update, and cleanup |
| `pytest_beehave/hatch.py` | Generates bee-themed demo `.feature` files |
| `pytest_beehave/plugin.py` | pytest plugin hook integration |
| `pytest_beehave/reporter.py` | Test reporting utilities |
| `pytest_beehave/html_steps_plugin.py` | HTML report step display |

---

## Domain Model

### Bounded Contexts

| Context | Responsibility | Key Modules |
|---------|----------------|-------------|
| `CLI` | Expose beehave as a command-line tool; dispatch subcommands | `pytest_beehave/__main__.py` |
| `Nest` | Bootstrap canonical directory structure and inject configuration | `pytest_beehave/nest.py`, `pytest_beehave/config.py` |
| `Config` | Read and write `[tool.beehave]` from pyproject.toml | `pytest_beehave/config.py` |
| `Sync` | Keep test stubs in sync with `.feature` files | `pytest_beehave/sync_engine.py`, `pytest_beehave/stub_writer.py`, `pytest_beehave/stub_reader.py` |
| `Parsing` | Parse `.feature` files into domain objects | `pytest_beehave/feature_parser.py` |
| `ID Generation` | Assign unique IDs to untagged Examples | `pytest_beehave/id_generator.py` |

### Entities

| Name | Type | Description | Bounded Context |
|------|------|-------------|-----------------|
| `NestConfig` | Value Object | Configuration for the nest command (features_dir, check, overwrite) | `Nest` |
| `NestResult` | Value Object | Result of running the nest command (created dirs, modifications, missing items) | `Nest` |
| `BootstrapResult` | Value Object | Result of bootstrapping the features directory | `Nest` |
| `ExampleId` | Value Object | An 8-char hex identifier for a Gherkin Example | `ID Generation` |
| `FeatureSlug` | Value Object | A Python-safe slug derived from a feature folder name | `Parsing` |
| `RuleSlug` | Value Object | A file-safe slug derived from a Rule block title | `Parsing` |
| `FeatureStage` | Enum | The lifecycle stage of a feature folder (backlog, in-progress, completed) | `Parsing` |
| `HatchFile` | Value Object | A single generated .feature file to be written | `Sync` |

### Actions

| Name | Actor | Object | Description |
|------|-------|--------|-------------|
| `nest` | `nest.py` module | `Path × NestConfig → NestResult` | Bootstraps directory structure, injects config, updates .gitignore |
| `inject_beehave_section` | `config.py` module | `Path → bool` | Injects `[tool.beehave]` into pyproject.toml if absent; returns True if modified |
| `bootstrap_features_directory` | `bootstrap.py` module | `Path → BootstrapResult` | Ensures canonical subfolder structure; migrates loose .feature files |
| `resolve_features_path` | `config.py` module | `Path → Path` | Resolves features directory path from config or default |
| `generate_hatch_files` | `hatch.py` module | `→ list[HatchFile]` | Generates bee-themed demo .feature files |

### Relationships

| Subject | Relation | Object | Cardinality | Notes |
|---------|----------|--------|-------------|-------|
| `BeehaveCLI.nest` | calls | `nest()` | 1:1 | CLI dispatches to domain function |
| `nest()` | calls | `inject_beehave_section()` | 1:1 | Config injection is part of nest workflow |
| `nest()` | uses | `NestConfig` | 1:1 | Config drives nest behavior |
| `nest()` | produces | `NestResult` | 1:1 | Result describes what was done |
| `BeehaveCLI` | uses | `fire.Fire` | 1:1 | Fire dispatches CLI to class methods |

### Module Dependencies

| Module | Depends On |
|--------|------------|
| `pytest_beehave/__main__.py` | `fire` (external), `pytest_beehave.nest` (internal) |
| `pytest_beehave/nest.py` | `pathlib` (stdlib), `dataclasses` (stdlib) |
| `pytest_beehave/config.py` | `tomllib` (stdlib), `pathlib` (stdlib) |
| `pytest_beehave/bootstrap.py` | `pathlib` (stdlib), `dataclasses` (stdlib) |
| `pytest_beehave/models.py` | `dataclasses` (stdlib), `enum` (stdlib) |
| `pytest_beehave/hatch.py` | `secrets` (stdlib), `pathlib` (stdlib), `dataclasses` (stdlib) |

---

## Active Constraints

- `fire` and `gherkin-official` are the only runtime dependencies beyond stdlib
- All production code lives in `pytest_beehave/` package
- `.feature` files are the source of truth; beehave never modifies test bodies
- Nest command is idempotent — additive, never removes or overwrites (unless `--overwrite` flag is set)
- Version format is calver (`major.minor.YYYYMMDD`)

---

## Key Decisions

- Use `fire` for CLI dispatch — class-based subcommands scale to the full command set (ADR-2026-04-23-cli-subcommand-structure)
- Nest logic lives in a separate `nest.py` module, not in `bootstrap.py` — SRP separation (ADR-2026-04-23-nest-module-placement)
- Pyproject.toml injection uses `tomllib` + string append — no new runtime deps (ADR-2026-04-23-pyproject-injection-strategy)
- Use `argparse` (stdlib) for CLI parsing — zero new dependencies (ADR-2026-04-22-cli-parser-library) — **superseded by fire-based CLI**
- Read version from `importlib.metadata` at runtime — single source of truth (ADR-2026-04-22-version-source)

---

## ADRs

See `docs/adr/` for the full decision record.

---

## Configuration Keys

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `[tool.beehave].features_path` | string | `"docs/features"` | Relative path to the features directory from project root |
| `[tool.beehave].framework` | string | `"pytest"` | Test framework for stub generation |
| `[tool.beehave].stub_format` | string | `"functions"` | Stub format: `"functions"` or `"classes"` |
| `[tool.beehave].show_steps_in_terminal` | bool | `true` | Display Gherkin steps in terminal output |
| `[tool.beehave].show_steps_in_html` | bool | `true` | Display Gherkin steps in HTML reports |

---

## External Dependencies

| Dependency | What it provides | Why not replaced |
|------------|------------------|-----------------|
| `fire` | CLI argument parsing and subcommand dispatch | Ergonomic class-to-CLI mapping; simpler than argparse for multi-command CLIs |
| `gherkin-official` | Gherkin `.feature` file parsing | Official parser; handles all Gherkin keywords and multi-language support |
| `tomllib` | TOML file reading | stdlib since Python 3.11; canonical API |
| `pathlib` | Filesystem path operations | stdlib; cross-platform path handling |
| `importlib.metadata` | Runtime package metadata access | stdlib; canonical API since Python 3.8 |

---

## Completed Features

See `docs/features/completed/` for accepted features.
