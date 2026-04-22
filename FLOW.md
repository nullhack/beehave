# FLOW — Feature Development Workflow

This file defines the static state machine for feature development. **Agents never modify this file.**
Only the stakeholder (human) may change it, using `skill flow` as the design protocol.
Dynamic work tracking lives in `WORK.md`.

---

## Work Variables

Every work item tracked in `WORK.md` must carry exactly these variables:

| Variable  | Description                                           |
|-----------|-------------------------------------------------------|
| `@id`     | The work item identifier (feature-stem or test @id)   |
| `@state`  | Current state in this workflow                        |
| `@branch` | Git branch where the work lives                       |

---

## Roles

These roles must exist before the workflow can run. Each state has exactly one owner.

| Role              | Agent File                             | Responsibility                                      |
|-------------------|----------------------------------------|-----------------------------------------------------|
| `product-owner`   | `.opencode/agents/product-owner.md`   | Discovery, scope, acceptance, `.feature` file moves |
| `system-architect`| `.opencode/agents/system-architect.md`| Architecture, domain design, adversarial review     |
| `software-engineer`| `.opencode/agents/software-engineer.md`| TDD loop, implementation, git, releases            |

---

## Prerequisites

All must be satisfied before starting any session. If any are missing, stop and alert the human.

| Requirement          | Verification Command                                      |
|----------------------|-----------------------------------------------------------|
| Role: product-owner  | `test -f .opencode/agents/product-owner.md`               |
| Role: system-architect | `test -f .opencode/agents/system-architect.md`          |
| Role: software-engineer | `test -f .opencode/agents/software-engineer.md`        |
| Skill: run-session   | `test -f .opencode/skills/run-session/SKILL.md`           |
| Skill: define-scope  | `test -f .opencode/skills/define-scope/SKILL.md`          |
| Skill: architect     | `test -f .opencode/skills/architect/SKILL.md`             |
| Skill: implement     | `test -f .opencode/skills/implement/SKILL.md`             |
| Skill: verify        | `test -f .opencode/skills/verify/SKILL.md`                |
| Skill: version-control | `test -f .opencode/skills/version-control/SKILL.md`     |
| Tool: uv             | `command -v uv`                                           |
| Tool: git            | `command -v git`                                          |
| Dir: docs/features/  | `test -d docs/features/backlog`                           |
| Dir: docs/adr/       | `test -d docs/adr`                                        |
| WORK.md              | `test -f WORK.md`                                         |

---

## State Machine

States are checked **in order**. The first matching condition is the current state.

```
[IDLE] ──► [STEP-1-BACKLOG-CRITERIA] (Stage 2 on backlog files — no WIP slot needed)

[IDLE] ──► [STEP-1-DISCOVERY] ──► [STEP-1-STORIES] ──► [STEP-1-CRITERIA]
                                                               │
                                                               ▼
[POST-MORTEM] ◄──────────────────────────────────── [STEP-2-READY]
     │                                                         │
     │                                                         ▼
     └──────────────────────────────────────────────► [STEP-2-ARCH]
                                                               │
                                                               ▼
                                                      [STEP-3-READY]
                                                               │
                                          ┌────────────────────┤
                                          ▼                    ▼
                                      [STEP-3-RED] ──► [STEP-3-GREEN]
                                                               │
                                                               ▼
                                                      [STEP-4-READY]
                                                               │
                                                               ▼
                                                      [STEP-5-READY]
                                                               │
                                                               ▼
                                                      [STEP-5-MERGE]
                                                               │
                                                               ▼
                                                      [STEP-5-COMPLETE]
                                                               │
                                                               ▼
                                                            [IDLE]
```

### Detection Rules (evaluated in order)

1. No file in `docs/features/in-progress/` AND any `backlog/` feature has `Status: BASELINED` but no `Example:` with `@id` → **[STEP-1-BACKLOG-CRITERIA]**
2. No file in `docs/features/in-progress/` → **[IDLE]**
3. Feature in `in-progress/`, no `Status: BASELINED` → **[STEP-1-DISCOVERY]**
4. Feature has `Status: BASELINED`, no `Rule:` blocks → **[STEP-1-STORIES]**
5. Feature has `Rule:` blocks, no `Example:` with `@id` → **[STEP-1-CRITERIA]**
6. Feature has `@id` tags, no `feat/` or `fix/` branch exists → **[STEP-2-READY]**
7. On feature branch, no test stubs in `tests/features/<stem>/` → **[STEP-2-ARCH]**
8. Test stubs exist, any have `@pytest.mark.skip` → **[STEP-3-READY]**
9. Unskipped test exists that fails → **[STEP-3-RED]**
10. All unskipped tests pass, skipped tests remain → **[STEP-3-GREEN]**
11. All tests pass, no skipped tests → **[STEP-4-READY]**
12. Manual state set by SA after Step 4 approval → **[STEP-5-READY]**
13. On main branch, feature still in `in-progress/` → **[STEP-5-MERGE]**
14. Post-mortem file exists for current feature → **[POST-MORTEM]**

---

## States

### [STEP-1-BACKLOG-CRITERIA]
**Owner**: `product-owner`
**Entry condition**: No file in `in-progress/` AND one or more `backlog/` features have `Status: BASELINED` but no `Example:` with `@id`
**Action**: Write `Rule:` blocks and `Example:` blocks with `@id` tags for BASELINED backlog features. Files stay in `backlog/` — do **not** move to `in-progress/`. No `WORK.md` entry required.
**Exit**: All BASELINED backlog features have `@id` tags → transition to `[IDLE]`
**Commit**: `feat(criteria): write acceptance criteria for <feature-stem>` per feature
**Note**: This state exists specifically for bulk Stage 2 work before a feature is selected for development. It does not consume the WIP slot. `run-session` must **not** treat this state as `[IDLE]` — there is work to do.

---

### [IDLE]
**Owner**: `product-owner`
**Entry condition**: No file in `docs/features/in-progress/` AND all BASELINED backlog features already have `@id` tags (or no BASELINED features exist)
**Action**: Select next BASELINED feature from `backlog/`; move it to `in-progress/`
**Exit**: Feature moved → create `WORK.md` entry with `@state: STEP-1-DISCOVERY`

---

### [STEP-1-DISCOVERY]
**Owner**: `product-owner`
**Entry condition**: Feature in `in-progress/`, no `Status: BASELINED`
**Action**: Interview stakeholder; update `scope_journal.md`, `discovery.md`, `glossary.md`
**Exit**: Feature baselined → update `@state: STEP-1-STORIES` in `WORK.md`
**Stay**: More discovery needed → remain in `[STEP-1-DISCOVERY]`

---

### [STEP-1-STORIES]
**Owner**: `product-owner`
**Entry condition**: Feature has `Status: BASELINED`, no `Rule:` blocks
**Action**: Write `Rule:` blocks with INVEST criteria
**Exit**: Stories committed → update `@state: STEP-1-CRITERIA` in `WORK.md`

---

### [STEP-1-CRITERIA]
**Owner**: `product-owner`
**Entry condition**: Feature has `Rule:` blocks, no `Example:` blocks with `@id`
**Action**: Write `Example:` blocks with `@id` tags; MoSCoW triage per example
**Exit**: Criteria committed → update `@state: STEP-2-READY` in `WORK.md`
**Commit**: `feat(criteria): write acceptance criteria for @id`

---

### [STEP-2-READY]
**Owner**: `system-architect`
**Entry condition**: Feature has `@id` tags, no `feat/<stem>` or `fix/<stem>` branch
**Action**: Create branch `feat/<stem>` from `main`; set `@branch` in `WORK.md`
**Exit**: Branch created → update `@state: STEP-2-ARCH` in `WORK.md`

---

### [STEP-2-ARCH]
**Owner**: `system-architect`
**Entry condition**: On `@branch`, no test stubs in `tests/features/<stem>/`
**Action**: Read feature; design domain stubs; write ADRs; update `system.md` (domain model + C4 sections); run `uv run task test-fast` to generate stubs
**Exit**: Stubs generated → update `@state: STEP-3-READY` in `WORK.md`
**Failure**: Spec unclear → escalate to `product-owner`; update `@state: STEP-1-DISCOVERY` in `WORK.md`
**Commit**: `feat(arch): design @id architecture`

---

### [STEP-3-READY]
**Owner**: `software-engineer`
**Entry condition**: Test stubs exist, some have `@pytest.mark.skip`
**Action**: Pick first skipped `@id`; remove skip; write test body
**Exit**: Test written and fails → update `@state: STEP-3-RED` in `WORK.md`

---

### [STEP-3-RED]
**Owner**: `software-engineer`
**Entry condition**: An unskipped test exists that fails
**Action**: Write minimal production code to pass the failing test
**Exit**: Test passes → update `@state: STEP-3-GREEN` in `WORK.md`

---

### [STEP-3-GREEN]
**Owner**: `software-engineer`
**Entry condition**: All unskipped tests pass; skipped tests remain
**Action**: Refactor if needed; then pick next `@id`
**Exit (more @ids)**: Next @id selected → update `@state: STEP-3-READY` in `WORK.md`
**Exit (all done)**: No skipped tests remain → update `@state: STEP-4-READY` in `WORK.md`
**Commit**: After each `@id` or logical group

---

### [STEP-4-READY]
**Owner**: `system-architect`
**Entry condition**: All tests implemented (no `@skip`) and passing
**Action**: Run all quality checks; semantic review against acceptance criteria
**Exit**: All checks pass → update `@state: STEP-5-READY` in `WORK.md`
**Failure**: Issues found → update `@state: STEP-3-READY` in `WORK.md`; document issues

---

### [STEP-5-READY]
**Owner**: `product-owner`
**Entry condition**: Manual state set by SA after Step 4 approval
**Action**: Demo and validate against acceptance criteria
**Exit**: Feature accepted → update `@state: STEP-5-MERGE` in `WORK.md`
**Failure**: Not accepted → update `@state: POST-MORTEM` in `WORK.md`

---

### [STEP-5-MERGE]
**Owner**: `software-engineer`
**Entry condition**: Feature accepted; still on `@branch`
**Action**: Merge `@branch` to `main` with `--no-ff`; delete `@branch`
**Exit**: Merged → update `@state: STEP-5-COMPLETE` in `WORK.md`

---

### [STEP-5-COMPLETE]
**Owner**: `product-owner`
**Entry condition**: On `main`, feature still in `in-progress/`
**Action**: Move feature from `in-progress/` to `completed/`
**Exit**: Feature moved → remove item from `WORK.md` active items; return to `[IDLE]`

---

### [POST-MORTEM]
**Owner**: `product-owner`
**Entry condition**: Post-mortem file exists for current feature
**Action**: Write post-mortem in `docs/post-mortem/`; create `fix/<stem>` branch from original start commit
**Exit**: Post-mortem committed → update `@state: STEP-2-ARCH`, `@branch: fix/<stem>` in `WORK.md`

---

## Session Protocol

### Session Start
1. Read `WORK.md` — find the active item; note `@id`, `@state`, `@branch`
2. Run auto-detection commands below to verify `@state` is correct
3. If detected state differs from `@state` in `WORK.md`, update `WORK.md` to match reality
4. Check prerequisites table above — if any missing, stop and report
5. Read the in-progress `.feature` file for `@id`
6. Run `git status` and `git branch --show-current` to confirm workspace matches `@branch`

### Session End
1. Update `WORK.md`: set `@state` to the new state; append to Session Log
2. Commit any uncommitted work:
   ```bash
   git add -A && git commit -m "WIP(@id): <what was done>"
   ```
3. If a step is fully complete, use the proper commit message instead of WIP

### State Transition Rule
Every state transition is owned by the agent who completes the current state.
Before doing any further work: update `WORK.md` first, then commit the update.

```bash
git add WORK.md && git commit -m "chore: @id transition to @state"
```

---

## Auto-Detection Commands

Run in order; first matching condition determines the state.

```bash
# 0. Check for STEP-1-BACKLOG-CRITERIA: no in-progress file AND backlog has BASELINED features without @id
NO_INPROGRESS=$(ls docs/features/in-progress/*.feature 2>/dev/null | grep -v ".gitkeep" | wc -l)
HAS_BASELINED_WITHOUT_IDS=$(grep -rl "Status: BASELINED" docs/features/backlog/ 2>/dev/null | xargs grep -L "@id:" 2>/dev/null | wc -l)
# If NO_INPROGRESS=0 AND HAS_BASELINED_WITHOUT_IDS>0 → [STEP-1-BACKLOG-CRITERIA]

# 1. Check for in-progress feature
ls docs/features/in-progress/*.feature 2>/dev/null | grep -v ".gitkeep"

# 2. Check feature baselined
grep -q "Status: BASELINED" docs/features/in-progress/*.feature

# 3. Check for Rule blocks
grep -q "^  Rule:" docs/features/in-progress/*.feature

# 4. Check for Example blocks with @id
grep -q "@id:" docs/features/in-progress/*.feature

# 5. Check for feature branch
git branch --show-current | grep -E "^feat/|^fix/"

# 6. Check for test stubs
ls tests/features/*/ 2>/dev/null | head -1

# 7. Check for skipped tests
grep -r "@pytest.mark.skip" tests/features/*/

# 8. Check test failures
uv run task test-fast 2>&1 | grep -E "FAILED|ERROR"
```

---

## Output Style

Every agent session must close with a `Next:` line — one concrete action, enough for a fresh agent to continue without questions.

- Report results, not process
- No narration around tool calls
- No restating tool output in prose
- No summaries of what was just done
