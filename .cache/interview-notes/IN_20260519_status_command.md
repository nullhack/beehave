# Interview Notes: beehave status Command

**Session:** IN_20260519_status_command
**Date:** 2026-05-19
**Stakeholder:** Project owner

## Pain Points

- `beehave check` produces a flat list of violations — no overview of which features are complete vs. need work
- With many features, impossible to tell at a glance which `beehave generate` to run, which tests to implement, which to fix
- `beehave list` shows scenarios but doesn't show development stage

## Business Goals

- Single `beehave status` command showing development stage of every feature
- CI gating: `--summary-only` exits 1 if any feature is not `ok`
- Machine-readable output via `--json` for scripting and pipelines
- `--stage <stage>` filtering for focused views

## Output Format

Tree-based hierarchy (Feature → Rule → Scenario), status in fixed left column, plain text labels.

### Scenario Status Labels

| Label | Meaning |
|-------|---------|
| `no test` | No test function exists for this scenario |
| `no body` | Test exists but body is empty (stub) |
| `N errors` | Test has body but check reports N problems |
| `ok` | Test exists, has body, passes check |

### Feature Stage Labels

| Label | Meaning |
|-------|---------|
| `broken` | Gherkin parse error |
| `no scenarios` | No Scenarios or Rules defined |
| `needs scenarios` | Rules exist but no Scenarios inside them |
| `needs tests` | Scenarios exist but no test files |
| `needs bodies` | Tests exist but all stubs |
| `needs fixes` | Tests have bodies but check reports errors |
| `ok` | All scenarios pass |

### Format Example

```
needs fixes     hive_activity (Hive Activity)
  ok            ├── honey production from nectar           (3 ex)
  2 errors      ├── Hive defense
  2 errors      │   ├── guard bee inspects visitor         scent, floral
  no body       │   └── guard bee inspects visitor2
  ok            └── Foraging
  ok                └── forager returns with nectar

  ok            comb_construction (Comb Construction)

needs bodies    dance_language (Waggle Dance Communication)
  no body       ├── round dance
  no body       └── waggle dance

no scenarios    future_ideas (Future Ideas)

needs scenarios temperature_control (Temperature Control)
  no scenarios  ├── Heating
  no scenarios  ├── Cooling
  no scenarios  └── Ventilation
```

### Format Rules

- Status on left, fixed-width column for vertical scanning
- Tree characters (`├──`, `│`, `└──`) for hierarchy
- `ok` features collapse to one line — no tree expansion
- Rule aggregate shows worst child with counts
- Scenario Outlines show example count: `(N ex)`
- Failing scenarios show violation names inline
- `--json` for machine-readable output
- `--summary-only` collapses to feature-level lines

## Edge Cases

- Malformed/empty Gherkin → `broken`
- Feature with only description, no children → `no scenarios`
- Feature with Rules but no Scenarios → `needs scenarios`
- Mixed-status feature: worst-scenario-wins for feature stage
- Orphaned test directories (no matching .feature) → reported separately
- Cross-feature function name collisions → detected in post-processing, annotated as warning

## Domain Terms

- **Feature:** a `.feature` file in `docs/features/`
- **Rule:** a Gherkin Rule within a feature
- **Scenario/Outline:** a Gherkin Scenario or Scenario Outline
- **Test file:** `*_test.py` in `tests/features/<feature_slug>/`
- **Test function:** `test_*` function in a test file
- **Stub:** test function body is only `pass` or `...`
- **beehave check:** verifies feature-test consistency (placeholders, literals, examples)
