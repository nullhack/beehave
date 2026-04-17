# Discovery: deprecation-sync

## State
Status: BASELINED

## Entities
| Type | Name | Candidate Class/Method | In Scope |
|------|------|----------------------|----------|
| Noun | `@deprecated` tag | Gherkin tag on an Example block | Yes |
| Noun | `@pytest.mark.deprecated` | pytest marker on a test function | Yes |
| Noun | backlog stage | `docs/features/backlog/` | Yes |
| Noun | in-progress stage | `docs/features/in-progress/` | Yes |
| Noun | completed stage | `docs/features/completed/` | Yes |
| Verb | detect deprecated | check Example tags for `@deprecated` | Yes |
| Verb | add marker | prepend `@pytest.mark.deprecated` to test function | Yes |
| Verb | remove marker | remove `@pytest.mark.deprecated` when tag is gone | Yes |

## Rules
- ALL 3 feature stages (backlog, in-progress, completed) are checked for `@deprecated` tag changes
- If an Example has `@deprecated` tag and the test function lacks `@pytest.mark.deprecated`, add the marker
- If an Example no longer has `@deprecated` tag and the test function has `@pytest.mark.deprecated`, remove the marker
- Deprecation sync never modifies test function bodies or parameter lists
- Deprecation sync is the ONLY operation performed on `completed/` feature test files

## Constraints
- Must handle the case where the test function does not exist (skip — stub sync handles creation)
- Must not add duplicate `@pytest.mark.deprecated` markers

## Questions
| ID | Question | Answer | Status |
|----|----------|--------|--------|
| Q1 | Should deprecation sync run even if stub sync is skipped for completed features? | Yes — deprecation sync always runs on all 3 stages regardless | ANSWERED |

## Architecture

### Module Structure

All changes live in `pytest_beehave/syncer.py`. No new modules are needed.

```
pytest_beehave/
  syncer.py   ← add _toggle_deprecated_marker, _sync_deprecated_markers_in_file,
                  extend _sync_one_feature to call deprecation sync for all stages
```

`plugin.py` requires **no changes** — `sync_stubs` is already the entry point and it calls `_sync_all_stages`.

### Key Decisions

**ADR-001: Deprecation sync lives in `syncer.py`, not a new module**

Decision: Add two private helpers to `syncer.py`; no new file.

Reason: The deprecation toggle is a sub-operation of stub sync — it reads the same `_Example.deprecated` field already parsed by `_parse_examples`, and it operates on the same test files. Extracting it to a new module would require passing `_Example` objects across a module boundary for no structural benefit (YAGNI + KISS).

Alternatives considered: A `deprecation.py` module — rejected because it would add indirection without reducing coupling; `syncer.py` already owns all file-manipulation logic.

---

**ADR-002: Deprecation sync runs as a second pass inside `_sync_one_feature`, not a separate top-level scan**

Decision: `_sync_one_feature` calls `_sync_deprecated_markers_in_file` after the stub-sync step (for `backlog`/`in-progress`) or instead of stub sync (for `completed`).

Reason: This keeps all per-feature-file logic in one place and avoids a second full directory walk. The `_parse_examples` call is already made by `_sync_active_feature`; for `completed`, we parse once and only toggle markers.

Alternatives considered: A separate `_sync_all_deprecated_markers` top-level pass — rejected because it would require a second full scan of all `.feature` files and all test files, doubling I/O for no benefit.

---

**ADR-003: Text-manipulation approach mirrors `gen_test_stubs.py`**

Decision: Use a regex `((?:@pytest\.mark\.\w+(?:\(.*?\))?\n)*)def test_\w+_{id_hex}\b` to capture the decorator block immediately before each test function, then add or remove `@pytest.mark.deprecated\n` from that block.

Reason: This is the proven approach already used in the `gen_test_stubs.py` tool. It is idempotent (add is a no-op if already present; remove is a no-op if absent), and it does not touch the function body or docstring.

Alternatives considered: AST-based manipulation — rejected because it would require `ast.unparse` which loses formatting; line-by-line scanning — rejected as more complex than the regex approach.

---

**ADR-004: `_sync_one_feature` returns a list of action strings (not a single `str | None`)**

Decision: Change `_sync_one_feature` return type from `str | None` to `list[str]` to accommodate multiple actions (stub sync action + deprecation action) from a single feature file.

Reason: A single feature file can now produce two distinct actions: `UPDATE <file>` (from stub sync) and `DEPRECATED <file>` (from deprecation toggle). The current `str | None` return type cannot represent both. Callers (`_sync_folder`) already use `extend`, so the change is minimal.

Alternatives considered: Keep `str | None` and fold deprecation into the existing action string — rejected because it conflates two distinct operations and makes the action log ambiguous.

---

### New Functions (signatures)

```python
def _toggle_deprecated_marker(content: str, id_hex: str, *, add: bool) -> str:
    """Add or remove @pytest.mark.deprecated before the test function for id_hex."""

def _sync_deprecated_markers_in_file(
    examples: list[_Example], test_file: Path
) -> str | None:
    """Toggle @pytest.mark.deprecated for all examples in one test file.
    Returns action string if file was changed, else None."""
```

### Interaction with Existing Functions

| Existing function | Change |
|---|---|
| `_sync_one_feature` | Return `list[str]`; call `_sync_deprecated_markers_in_file` for all stages |
| `_sync_folder` | No change needed — already uses `extend` on results |
| `_sync_active_feature` | No change — still handles stub create/update |
| `_update_stub_file` / `_transform_stub_content` | No change — stub sync and deprecation sync are separate passes |
| `plugin.py` | No change |

### Build Changes (needs PO approval: no)

No new runtime dependencies. No entry point changes.
