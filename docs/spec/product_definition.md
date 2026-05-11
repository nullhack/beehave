# Product Definition: beehave

> **Status:** BASELINED (2026-05-10)
> Fill in each section during Discovery. Replace placeholders with project-specific content.
> This document is the single source of truth for project scope and conventions.

---

## What beehave IS

- A thin Python library that adds Gherkin-style step decorators (@Given, @When, @Then, @And, @But) to Hypothesis-based tests
- A vocabulary enforcement layer that validates test step descriptions against .feature file step text at collection time
- A traceability bridge that links test functions to .feature scenarios via @id tags
- A Gherkin parser that maps Scenario Outline + Examples to Hypothesis @example + @given
- A failure reporting layer that renders Gherkin-readable failure output from Hypothesis counterexamples

## What beehave IS NOT

- Does NOT provide an assertion DSL — Python's assert and pytest's assertion introspection handle assertions
- Does NOT execute step definitions — the test body is plain Python, not a step definition runner
- Does NOT replace Hypothesis — @given remains the data generation mechanism; beehave composes with it
- Does NOT wrap Hypothesis in a monolithic decorator — step decorators apply @given at import time via standard Python mechanics
- Does NOT do natural language processing or synonym resolution — vocabulary enforcement is exact matching
- Does NOT couple to a domain model — domain terms come from .feature files, not class introspection
- Does NOT require pytest for core functionality — the core is runner-agnostic, using Hypothesis directly

## Why does this exist

Existing BDD frameworks (pytest-bdd, behave) force splitting one scenario across multiple step definition functions, requiring exact string matching that makes Gherkin verbose and brittle. Hypothesis users who want Gherkin structure have no bridge between property-based testing and BDD. beehave provides "one function, one scenario" with @id-based traceability instead of string matching, collection-time vocabulary validation instead of manual review, and Hypothesis integration via standard Python decorator mechanics instead of wrapping.

## Users

- **Property-Based TDD Developer** — Uses Hypothesis daily for property-based testing; wants Gherkin structure and traceability without leaving Python; values type safety, collection-time validation, and zero runtime overhead
- **QA Engineer** — Writes .feature files in Gherkin; wants to verify that every scenario has a corresponding test; needs traceability from .feature scenarios to test functions; may not write Python but needs to understand test coverage
- **Team Lead** — Wants vocabulary enforcement to keep the test suite consistent; needs to see which .feature scenarios are covered by tests; values progressive adoption

## Quality Attributes

| Attribute | Scenario | Target | Priority |
|-----------|----------|--------|----------|
| Performance | When pytest collects tests, vocabulary and step validation runs during collection phase; on test failure, step text is rendered with counterexample values for Gherkin-readable output | Collection-time validation must add <1ms per test to collection; runtime overhead must be zero on pass, report rendering only on failure | Must |
| Composability | When a developer uses beehave decorators alongside Hypothesis @given, @example, and @settings, both work together without conflict | beehave decorators must compose with all standard Hypothesis decorators; no wrapping or interception of Hypothesis internals | Must |
| Progressive Adoption | When a developer writes a test with only @Given/@When/@Then decorators and no .feature file, the test must still run correctly | Tests must work at adoption level 1 (decorators only) without .feature files, strategy variables, or @example values | Must |
| Correctness | When pytest collects a test with an @id tag, beehave must validate the link between the .feature scenario and the test function | @id linking must be validated at collection time; mismatches must produce clear error messages | Must |
| Runner-Agnosticism | When a developer uses beehave without pytest, core features (decorators, strategy resolution, reporting) must still work | The core library must not import pytest; Hypothesis is the only required dependency for core functionality | Must |
| Usability | When a developer writes a test with <placeholder> names, beehave must resolve strategies with zero configuration for the common case | Module-level variable resolution must work by name matching without registration or configuration | Should |
| Idempotency | When any CLI command (sync, generate, fix, clean) is run twice, the result is the same as running once | All commands produce idempotent results | Must |
| Safety | When a developer runs a CLI command without flags, no destructive action occurs | sync and generate are safe by default; fix supports --dry-run; clean requires confirmation | Must |

---

## Out of Scope

- Assertion DSL or custom assertion types — Python's assert is sufficient
- Step definition files — beehave uses "one function, one scenario" instead
- Natural language processing or synonym resolution — exact matching only
- Domain model introspection — domain terms come from .feature files, not Python classes
- Full BDD framework replacing behave/pytest-bdd — beehave validates and traces, it doesn't execute .feature files
- Monolithic @gherkin decorator — step decorators compose with Hypothesis, they don't wrap it
- Hypothesis settings in .feature files — settings belong in pyproject.toml or @settings, not in stakeholder-facing Gherkin
- Inline strategy kwargs on decorators — all five decorators take only a step text string

## Delivery Order

1 → 2a → 2b → 2c → 2d → 3a → 3b → 4 (each level depends on the previous)

1. **Step Decorators + Strategy Resolution** — @Given, @When, @Then, @And, @But decorators that attach metadata and apply @given at import time; @Example decorator for explicit test values; @Background decorator for shared setup; strategy resolution from module-level variables and @Example type inference
2a. **Traceability — @id Tags and Sync** — @id linking between .feature scenarios and test functions; beehave sync command; orphan detection
2b. **Traceability — Generate Core** — beehave generate command for test stub creation; test function naming convention; idempotency; conflict handling
2c. **Traceability — Generate Modes** — beehave generate output modes (--json, non-TTY); scope selection; edge case handling (empty features, malformed files)
2d. **Traceability — Fix and Clean** — beehave fix (decorator alignment) and beehave clean (orphan removal); escalate in risk
3a. **Feature Parsing — File Mapping + Step Text** — .feature file to test module mapping (Rule-based); exact step text matching between .feature and decorators
3b. **Feature Parsing — Ordering + Placeholders + Adoption** — step ordering validation (Given→When→Then); placeholder-parameter matching; progressive adoption levels
4. **Failure Reporting** — Gherkin-readable failure reports via Hypothesis report_example callback; step rendering with counterexample values; Then-failed and line-number heuristics
5. **Self-Validation Fixes** — generate() output observability (file paths); clean import blocks on append; __init__.py creation; skip markers on stubs; step decorators in stubs; strategy fallback warnings

---

## Project Conventions

### Definition of Done

All criteria must be met before a feature is considered done.

**Development:**

- [ ] All BDD scenarios from the .feature file pass
- [ ] Quality Gate passes all three tiers (Design → Structure → Conventions)
- [ ] Test coverage meets project threshold (≥ 80%)
- [ ] No test coupling — tests verify behavior, not structure
- [ ] Production code uses ubiquitous language from glossary.md

**Review:**

- [ ] Code Review approved by R (independent reviewer)
- [ ] Acceptance Testing passed — PO verifies BDD scenarios behave as expected

**Deployment:**

- [ ] Version bumped in pyproject.toml
- [ ] CHANGELOG.md updated

### Deployment

**Deployment type:** Library

#### Common (all deployment types)

- [ ] Version bumped in pyproject.toml
- [ ] CHANGELOG.md updated with version and delivered scenarios
- [ ] Git tag created (format: `v<semver>`)

#### Library

- [ ] Package builds without errors (`python -m build`)
- [ ] Package published to PyPI (`twine upload dist/*`)
- [ ] Installable from PyPI in clean environment

### Branch Strategy

- **Convention:** Trunk-based (short-lived feature branches from trunk, PR before merge)
- **Branch naming:** `<type>/<feature-id>-<short-description>` (e.g., `feature/step-decorators`)
- **Merge policy:** Squash merge to trunk after approval

---

## Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Language | Python ≥3.14 | Project requirement |
| Test Framework | Hypothesis | Property-based testing; beehave composes with it |
| Test Runner | pytest (optional) | Integration via plugin; core is runner-agnostic |
| CLI | Click or Typer | CLI commands for sync, generate, fix, clean |
| Gherkin Parser | Custom implementation | No existing parser supports the full Gherkin spec needed |

---

## Dependencies

| Dependency | Type | What it provides | Why not replaced |
|------------|------|------------------|-----------------|
| hypothesis | required | Property-based testing engine, @given/@example/@settings decorators, report_example callback, shrinking | Core dependency; beehave composes with it, not wraps it |
| click (or typer) | required | CLI framework for sync/generate/fix/clean commands | Standard CLI library for Python |
| pytest | optional (plugin) | Test runner, collection hooks, reporting | Most popular Python test runner; beehave provides an optional plugin; core works without it |

---

## Scope Changes

| Date | Session | Change | Reason |
|------|---------|--------|--------|
| 2026-05-10 | IN_20260510_design | Initial product definition | Core product design decisions |
| 2026-05-10 | IN_20260510_architecture | Core library is runner-agnostic | Founder identified that tying to pytest would limit beehave |
| 2026-05-10 | IN_20260510_integration | Failure reporting via Hypothesis callback | Uses Hypothesis's own extension points, not pytest hooks |