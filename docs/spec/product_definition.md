# Product Definition: beehave

> **Status:** BASELINED (2026-05-13)
> This document is the single source of truth for project scope and conventions.

---

## What beehave IS

- A code generator (`beehave generate`) that produces pure Hypothesis `@given()`/`@example()` stubs from Gherkin `.feature` files — one feature per invocation
- A consistency checker (`beehave check`) that re-parses features, AST-parses tests, joins by function name, and reports violations in machine-parseable format
- A cleanup tool (`beehave clean`) that removes unmapped test functions — retains import block even if all functions are removed, never deletes the file
- A status reporter (`beehave status`) that computes and displays the development stage of every feature in a project

## What beehave IS NOT

- Does NOT act as a test runner, runtime framework, step-definition engine, or assertion DSL
- Does NOT resolve synonyms or replace Hypothesis in any way
- Does NOT provide `--dry-run` preview (acknowledged as future enhancement, not v3 scope)
- Does NOT manage cache/state, format code, or lint

## Why does this exist

Python developers using Gherkin for behavior specification need their test code to stay synchronized with their feature files. Existing BDD tools inject runtime frameworks into test code, creating coupling and fragility. beehave generates plain Hypothesis tests with zero imports from beehave itself, and enforces consistency through AST-based checking — giving developers spec-to-test traceability without framework lock-in.

## Users

- **Python developer** — Writes Gherkin feature files and wants generated Hypothesis test stubs that stay consistent with those specs. Uses `generate`, `check`, and `clean` during the development cycle.

## Quality Attributes

| Attribute | Scenario | Target | Priority |
|-----------|----------|--------|----------|
| Correctness | When `check` maps scenarios to test functions, the function-name derivation is deterministic and produces a bijection | 100% deterministic mapping, zero ambiguity | Must |
| Reliability | When any command encounters an error, it reports immediately and exits non-zero | Zero partial output on failure | Must |
| Simplicity | When tests are generated, they import only `hypothesis` — never `beehave` | Zero beehave imports in generated test code | Must |
| Composability | When external tooling consumes beehave's function APIs, they remain stable across versions | Public API documented and backward-compatible | Should |

---

## Out of Scope

- Test runner or execution engine
- Runtime framework or step-definition system
- Assertion DSL or synonym resolution
- `--dry-run` preview mode
- Plugin system (APIs are designed for future composability but no plugin interface in v3)
- Code formatting or linting
- Cache or state management

---

## Project Conventions

### Definition of Done

All criteria must be met before a feature is considered done.

**Development:**

- [ ] All BDD scenarios from the .feature file pass
- [ ] Quality Gate passes all three tiers (Design → Structure → Conventions)
- [ ] Test coverage meets project threshold (≥ 80%)
- [ ] No test coupling — tests verify behavior, not structure
- [ ] Production code follows priority order: YAGNI > DRY > KISS > OC > SOLID > Design Patterns
- [ ] Code uses ubiquitous language from glossary.md

**Review:**

- [ ] CI pipeline passes all three tiers (Design → Structure → Conventions)
- [ ] Code Review approved by R (independent reviewer, not the SE who wrote the code)
- [ ] Acceptance Testing passed — PO verifies BDD scenarios behave as expected

**Deployment:**

- [ ] Release Verification checklist completed
- [ ] CHANGELOG.md updated

### Deployment

**Deployment type:** CLI

#### Common (all deployment types)

- [ ] Version bumped in pyproject.toml
- [ ] CHANGELOG.md updated with version and delivered scenarios
- [ ] Git tag created (format: `v<semver>`)

#### CLI / Library

- [ ] Package builds without errors (`python -m build`)
- [ ] Package published to PyPI (`twine upload dist/*`)
- [ ] Installable from PyPI in clean environment

### Branch Strategy

- **Convention:** Trunk-based (short-lived feature branches from trunk, PR before merge)
- **Branch naming:** `feature/<short-description>` (e.g., `feature/gherkin-parser`)
- **Merge policy:** Squash merge to trunk after approval

---

## Scope Changes

| Date | Session | Change | Reason |
|------|---------|--------|--------|
| 2026-05-13 | IN_20260513_discovery | Initial product definition baselined from v3 spec | Discovery phase kickoff |
