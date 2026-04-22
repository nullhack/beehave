# Discovery: beehave

> Append-only session synthesis log.
> Written by the product-owner at the end of each discovery session.
> Each block records one session: a summary paragraph and a table of features whose behavior changed.
> A row appears only when a `.feature` file would be updated as a result of the session.
> Confirmations of existing behavior are not recorded here — see `docs/scope_journal.md` for the full Q&A.
> Never edit past blocks — later blocks extend or supersede earlier ones.

---

## Session 2026-04-21

**Summary**: Session 1 established the full project scope for beehave: a framework-agnostic CLI and Python library that keeps Gherkin `.feature` files in sync with test stubs. Covered all general questions (users, purpose, success/failure, out-of-scope), all cross-cutting concerns (framework selection, config, output modes, test identity, feature stage mapping), and per-feature Q&A for all 15 planned features. A same-day supplement corrected `deprecation-sync` cascade behavior (absolute, no override in v1) and defined `hatch` demo content (bee-themed, covers Feature/Rule/Example/Scenario Outline).

| Feature | Change | Source questions | Reason |
|---------|--------|-----------------|--------|
| `nest` | created | Q8: "What CLI commands exist?" → nest bootstraps dirs; Q8a: "--check mode?" → CI dry-run; per-feature Q&A | New behavior: additive/idempotent directory + pyproject.toml init with --check and --overwrite modes |
| `id-generation` | created | I1: "@id format?" → 8-char hex; I1a: human-assigned IDs valid; I2: "malformed?" → replace in place | New behavior: assigns stable @id tags to untagged/malformed Examples; project-wide uniqueness |
| `status` | created | Q8: "beehave status?" → dry-run preview; C8: "output modes?" → silent/verbose/json; exit 0/1 | New behavior: dry-run of what sync would change; Unix exit codes for CI |
| `cache-management` | created | per-feature Q&A: JSON cache path, auto-rebuild on stale/corrupt, added to .gitignore by nest | New behavior: incremental sync cache at .beehave_cache/features.json |
| `template-customization` | created | C7: "template customization?" → yes, custom folder fully replaces built-in; --template-dir or template_path | New behavior: user-defined stub templates via flag or config key |
| `sync-create` | created | C9: "stub identity?" → test_<slug>_<id>; SC2: "one file per Rule"; per-feature Q&A | New behavior: generates new skipped test stubs for Examples with no existing test |
| `sync-update` | created | per-feature Q&A: update docstring/name/deprecated marker; never touch body; warn on Outline column change | New behavior: updates stubs on Example change; preserves test body always |
| `sync-cleanup` | created | C5: "deleted feature?" → warn (configurable); per-feature Q&A: orphans, misplaced stubs | New behavior: warns orphans, moves misplaced stubs, warns on deleted feature files |
| `adapter-contract` | created | C1: "framework selection?" → explicit flag, default pytest; Q9: "framework adapters?"; per-feature Q&A | New behavior: defines the FrameworkAdapter interface; v1 = pytest only |
| `pytest-adapter` | created | per-feature Q&A: skip/deprecated/parametrize markers; function prefix test_; return -> None; body ... | New behavior: built-in pytest adapter implementing the contract |
| `parameter-handling` | created | Q7: "Scenario Outlines?" → parametrized stubs; per-feature Q&A: warn-only on column change | New behavior: parametrized stubs for Scenario Outlines; column change = warn only |
| `unittest-adapter` | created | Q7: "unittest in v1?" → PARKED for v2 | Feature registered as out-of-scope for v1; no implementation |
| `hatch` | created | Q8: "beehave hatch?" → demo content; supplement: bee-themed, covers Feature/Rule/Example/Outline | New behavior: generates bee-themed demo .feature files |
| `config-reading` | created | C3: "config location?" → pyproject.toml [tool.beehave]; C1: framework key; C7: template_path key | New behavior: reads [tool.beehave] from pyproject.toml and applies defaults |
| `deprecation-sync` | created | supplement: cascade behavior → absolute, no per-Example override in v1 | New behavior: propagates @deprecated tags absolutely from Feature/Rule to all child Examples |
