# Changelog

## [1.0.0] — 2026-05-20

### Added

- **Title Validation** — `beehave check` and `beehave generate` now validate Feature, Rule, and Scenario titles across all `.feature` files.
  - Charset: `[\w\s]+` (word characters and spaces only)
  - Word count: 2–6 words
  - Uniqueness: case-insensitive global comparison across all title types
  - 6 new violation types: `invalid-feature-title`, `invalid-rule-title`, `invalid-scenario-title`, `duplicate-feature-title`, `duplicate-rule-title`, `duplicate-scenario-title`
  - `generate_stubs()` blocks generation on title violations (pre-flight gate)
  - `check_all()` includes title violations alongside scenario-level violations

- **Case-Insensitive Matching** — Placeholder and literal comparison are now case-insensitive.
  - `ph.name.lower()` comparison for placeholders (`<Dog>` matches `dog`, `DOG`)
  - `str(lit.value).lower()` comparison for literals (`"Rex"` matches `"rex"`, `int(77000)` matches `Decimal("77000")`)
  - Negative numbers visible in test bodies (`-2010` from `UnaryOp` folding)
  - Quoted placeholders no longer double-captured as both placeholder and literal
  - Bracket notation `[something]` preserved as literal content

- **Status Command** (`beehave status`) — Reports the development stage of every feature in a project.
  - 7-stage decision tree: `broken` → `no scenarios` → `needs scenarios` → `needs tests` → `needs bodies` → `needs fixes` → `ok`
  - Tree-based output format with per-scenario status labels (`ok`, `no body`, `N errors`, `no test`)
  - Rule aggregation with comma-joined child counts (`"1 no body, 2 errors"`)
  - `--json` flag for machine-readable output
  - `--include-unmapped` flag to show unmapped test directories
  - Exit codes: 0 (all ok), 1 (any not ok), 2 (fatal error)

### Changed

- All test fixture titles updated to 2+ words for title validation compliance
- `OrphanedDir` renamed to `UnmappedDir`, `--include-orphaned` → `--include-unmapped` across all modules
- Product definition expanded to include status reporter
- `.cache/` added to `.gitignore`

### Fixed

- Literal extraction type mismatch: `int(77000)` from Gherkin now matches `Decimal("77000")` in test bodies
- Negative number constants from `ast.UnaryOp` now correctly extracted from test bodies
- Quoted `<placeholder>` tokens no longer double-captured as both placeholder and literal
