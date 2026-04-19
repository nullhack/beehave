---
name: session-workflow
description: Session start and end protocol — read TODO.md, continue from checkpoint, update and commit
version: "4.0"
author: software-engineer
audience: all-agents
workflow: session-management
---

# Session Workflow

Every session starts by reading state. Every session ends by writing state. This makes any agent able to continue from where the last session stopped.

## Agent Responsibilities: Feature File Moves

**The PO is the sole owner of all `.feature` file moves.** Software-engineer and reviewer never move, rename, or create feature files.

| Trigger | Action | Who |
|---|---|---|
| Feature selected for development | Move `backlog/<name>.feature` → `in-progress/<name>.feature` | PO only |
| Step 5 acceptance | Move `in-progress/<name>.feature` → `completed/<name>.feature` | PO only |

**Escalation**: if software-engineer or reviewer find no file in `docs/features/in-progress/`, they **stop immediately** and output:

> No feature is currently in progress. Escalating to @product-owner — please move a BASELINED feature from `docs/features/backlog/` to `docs/features/in-progress/` to begin development.

## Session Start

1. Read `TODO.md` — find current feature, current step, and the "Next" line.
   - If `TODO.md` does not exist, create a basic one:
     ```markdown
     # Current Work

     No feature in progress.
     Next: Run @<product-owner-agent> — load skill feature-selection and pick the next BASELINED feature from backlog.
     ```
2. **If you are the PO** and Step 1 (SCOPE) is active: check `docs/discovery_journal.md` for the most recent session block.
   - If the most recent block has `Status: IN-PROGRESS` → the previous session was interrupted. Resume it before starting a new session: finish updating `.feature` files and `docs/discovery.md`, then mark the block `Status: COMPLETE`.
3. If a feature is active at Step 2–5, read:
   - `docs/features/in-progress/<name>.feature` — feature spec (feature description + Rules + Examples)
   - `docs/discovery.md` — project-level discovery changelog (for context)
4. Run `git status` — understand what is committed vs. what is not
5. Confirm scope: you are working on exactly one step of one feature

**If TODO.md says "No feature in progress":**

- **PO**: Load `skill feature-selection` — it guides you through scoring and selecting the next BASELINED backlog feature. You must verify the feature has `Status: BASELINED` before moving it to `in-progress/`. Only you may move it.
- **Software-engineer or reviewer**: Update TODO.md `Next:` line to `Run @<product-owner-agent> — load skill feature-selection and pick the next BASELINED feature from backlog.` Then **stop**. Never self-select a feature. Never move a `.feature` file.

## Session End

1. Update TODO.md:
   - Mark completed criteria `[x]`
   - Mark in-progress criteria `[~]`
   - Update the "Next" line with one concrete action
2. Commit any uncommitted work (even WIP):
   ```bash
   git add -A
   git commit -m "WIP(<feature-name>): <what was done>"
   ```
3. If a step is fully complete, use the proper commit message instead of WIP.

## Step Completion Protocol

When a step completes within a session:

1. Update TODO.md to reflect the completed step before doing any other work.
2. Commit the TODO.md update:
   ```bash
   git add TODO.md
   git commit -m "chore: complete step <N> for <feature-name>"
   ```
3. Only then begin the next step (in a new session where possible — see Rule 4).

## TODO.md Format

```markdown
# Current Work

Feature: <name>
Step: <1-5> (<step name>)
Source: docs/features/in-progress/<name>.feature

## Progress
- [x] `@id:<hex>`: <description>
- [~] `@id:<hex>`: <description>  ← IN PROGRESS
- [ ] `@id:<hex>`: <description>

## Next
Run @<agent-name> — <one concrete action>
```

**"Next" line format**: Always prefix with `Run @<agent-name>` so the human knows exactly which agent to invoke. Agent names are defined in `AGENTS.md` — use the name exactly as listed there. Examples:
- `Run @<software-engineer-agent> — implement @id:a1b2c3d4 (Step 3 RED)`
- `Run @<software-engineer-agent> — load skill implementation and begin Step 2 (Architecture) for <feature-name>`
- `Run @<reviewer-agent> — verify feature <feature-name> at Step 4`
- `Run @<product-owner-agent> — pick next BASELINED feature from backlog`
- `Run @<product-owner-agent> — accept feature <feature-name> at Step 5`

**Source path by step:**
- Step 1: `Source: docs/features/backlog/<name>.feature`
- Steps 2–4: `Source: docs/features/in-progress/<name>.feature`
- Step 5: `Source: docs/features/completed/<name>.feature`

Status markers:
- `[ ]` — not started
- `[~]` — in progress
- `[x]` — complete
- `[-]` — cancelled/skipped

When no feature is active:
```markdown
# Current Work

No feature in progress.
Next: Run @<product-owner-agent> — load skill feature-selection and pick the next BASELINED feature from backlog.
```

## Step 1 (Stage 2 Criteria) Self-Declaration

When Stage 2 Step B (criteria) is complete and before the `feat(criteria):` commit, the PO produces a Self-Declaration as **conversation output only** — do not write it into TODO.md:

```
PO Self-Declaration — <feature-name>
* INVEST-I: each Rule is Independent — AGREE/DISAGREE | conflict:
* INVEST-V: each Rule delivers Value to a named user — AGREE/DISAGREE | Rule:
* INVEST-S: each Rule is Small enough for one development cycle — AGREE/DISAGREE | Rule:
* INVEST-T: each Rule is Testable — AGREE/DISAGREE | Rule:
* Observable: every Then is a single, observable, measurable outcome — AGREE/DISAGREE | file:line
* No impl details: no Example tests internal state or implementation — AGREE/DISAGREE | file:line
* Coverage: every entity in the feature description appears in at least one Rule — AGREE/DISAGREE | missing:
* Distinct: no two Examples test the same observable behavior — AGREE/DISAGREE | file:line
* Unique IDs: all @id values are unique within this feature — AGREE/DISAGREE
* Pre-mortem: I ran a pre-mortem on each Rule and found no hidden failure modes — AGREE/DISAGREE | Rule:
* Scope: no Example introduces behavior outside the feature boundary — AGREE/DISAGREE | file:line
```

Every `DISAGREE` is a hard blocker — fix before committing.

## Step 3 (TDD Loop) Cycle-Aware TODO Format

During Step 3 (TDD Loop), TODO.md **must** include a `## Cycle State` block to track Red-Green-Refactor progress.

When `Phase: REFACTOR` is complete for all @id, the SE produces a Self-Declaration as **conversation output only** (not in TODO.md) before handing off to Step 4.

```markdown
# Current Work

Feature: <name>
Step: 3 (TDD Loop)
Source: docs/features/in-progress/<name>.feature

## Cycle State
Test: `@id:<hex>` — <description>
Phase: RED | GREEN | REFACTOR

## Progress
- [x] `@id:<hex>`: <description>
- [~] `@id:<hex>`: <description>          ← in progress (see Cycle State)
- [ ] `@id:<hex>`: <description>          ← next

## Next
<One actionable sentence>
```

### Phase Transitions

- Move from `RED` → `GREEN` when the test fails with a real assertion
- Move from `GREEN` → `REFACTOR` when the test passes
- Move from `REFACTOR` → mark `@id` complete in `## Progress` when test-fast passes

## Rules

1. Never skip reading TODO.md at session start
2. Never end a session without updating TODO.md
3. Never leave uncommitted changes — commit as WIP if needed
4. One step per session where possible; do not start Step N+1 in the same session as Step N
5. The "Next" line must be actionable enough that a fresh AI can execute it without asking questions
6. During Step 3, always update `## Cycle State` when transitioning between RED/GREEN/REFACTOR phases
7. When a step completes, update TODO.md and commit **before** any further work
8. During Step 3, produce the Self-Declaration as conversation output after all quality gates pass — every claim must have AGREE/DISAGREE with `file:line` evidence; never write it into TODO.md
9. During Step 1 Stage 2 Step B (criteria), produce the PO Self-Declaration as conversation output before the criteria commit — every DISAGREE is a hard blocker; never write it into TODO.md
