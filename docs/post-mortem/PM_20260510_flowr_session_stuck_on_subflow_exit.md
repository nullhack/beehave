# PM_20260510_flowr_session_stuck_on_subflow_exit: Flowr session stuck on subflow exit — wrong command form used

## Failed At

review-gate → done transition in `development-flow`, within the `step-decorators-dev` session. The orchestrator successfully computed the transition `review-gate → done` with `committed=verified`, but the session remained stuck at `review-gate` because the wrong command form was used. Subsequent `session set-state` attempts to reach `done`, `delivery`, or `acceptance` all failed because those states belong to different flows and `set-state` doesn't handle stack pops.

The orchestrator then worked around the issue by manually creating a new `step-decorators-delivery` session at `feature-development-flow` / `acceptance`, leaving the original `step-decorators-dev` session orphaned at `review-gate`.

## Root Cause

Flowr has **two** transition command forms with fundamentally different behaviors:

| Form | Command | Session-aware? | Stack handling | Use case |
|------|---------|---------------|---------------|----------|
| Explicit | `flowr transition <flow> <state> <trigger>` | No | None | What-if queries, debugging |
| Session | `flowr transition <trigger> --session` | Yes | Auto push/pop on subflow enter/exit | Normal flow navigation |

The orchestrator used the **explicit** form (`flowr transition development-flow review-gate pass --evidence committed=verified`). This form:

1. Loads the flow definition from file
2. Validates conditions against evidence
3. Computes and prints the target state (`done`)
4. **Does NOT update any session** — it is read-only
5. **Does NOT pop the stack** — it doesn't even have access to session state

When the subflow (`development-flow`) reaches an exit state (`done`), the session-aware form (`--session`) automatically:

1. Detects the target is in the flow's `exits` list
2. Pops the session stack to return to the parent flow (`feature-development-flow`)
3. Resolves the parent's `next` mapping: `development.done → delivery`
4. Auto-enters the new subflow (`delivery-flow`)
5. Saves the updated session

The explicit form did none of this. The orchestrator then compounded the error by trying `session set-state`, which is a manual override that also doesn't interact with the stack.

### Why this happened

The AGENTS.md and skill instructions reference `flowr transition` without consistently distinguishing the two forms. The explicit form's output (`from → trigger → to`) looks like a successful state change, creating a false sense of completion. The orchestrator treated the JSON output as confirmation that the state change was persisted, when in fact it was only a computation.

## Missed Gate

The **procedural contract** gate: "Every state transition must go through flowr." The transition was computed but never applied to a session. The orchestrator violated the rule by using a read-only diagnostic command as if it were a state-changing operation.

## Fix

### 1. Always use `--session` for state transitions

The only correct command for moving through a flow is:

```bash
python -m flowr transition <trigger> --session --evidence <key>=<value>
```

The explicit form (`flowr transition <flow> <state> <trigger>`) is for **inspection only** — checking what a transition would produce without side effects. Never use it to advance flow state.

### 2. Recognize exit states

When a transition target is an exit state (listed under `exits:` in the flow YAML), the `--session` form handles everything automatically: stack pop, parent resolution, subflow re-entry. No manual intervention is needed.

### 3. Never use `session set-state` for normal navigation

`session set-state` is a recovery tool that bypasses all transition logic, condition checking, and stack management. It should only be used when a session is corrupted and needs manual correction. After using it, verify the session state is consistent with `flowr session show`.

### 4. Clean up orphaned sessions

The `step-decorators-dev` session at `review-gate` is now stale — the feature has progressed to delivery via the workaround session. This session should be archived or removed to avoid confusion.

## Restart Check

1. Before any `flowr transition`, confirm the command includes `--session`
2. After any transition, verify the session was updated: `flowr session show --name <name>`
3. If a transition target is an exit state, trust `--session` to handle the stack automatically — do not attempt manual `set-state` calls
4. If a session appears stuck, check `flowr session show` for stack state before attempting manual overrides