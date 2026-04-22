# Post-Mortem: Stage 2 Specification — Infinite Loop

**Date**: 2026-04-22
**Feature stem**: all-backlog-features
**Keyword**: infinite-loop
**Author**: product-owner

## What happened

A task was launched asking the product-owner subagent to write Stage 2 (Rules + Examples) for
all 14 backlog features. The agent loaded `skill run-session`, which detected `FLOW.md` state
as `[IDLE]` (no file in `in-progress/`). The idle protocol instructed the agent to load
`skill select-feature` and find a BASELINED feature. No features were BASELINED (all had
`Status: ELICITING`). The agent escalated to PO — which is itself — and re-entered the same
loop. The task was aborted externally.

## Root causes (3)

1. **Features were never BASELINED.** All 14 features had `Status: ELICITING`. Stage 2 is
   gated on `Status: BASELINED`. The stakeholder approval step was skipped after discovery.

2. **FLOW.md has no detection rule for Stage 2 on backlog files.** Writing Rules + Examples
   for features that sit in `backlog/` (not `in-progress/`) is a valid workflow state, but
   no state covers it. The agent fell through to `[IDLE]` and looped.

3. **`run-session` hijacks subagent context.** The product-owner agent always loads
   `run-session` at start, which evaluates `FLOW.md` and takes over control flow regardless
   of what the task prompt says. Custom task instructions cannot override this.

## Fix applied

- Added `[STEP-1-BACKLOG-CRITERIA]` state to `FLOW.md` covering Stage 2 work on backlog files.
- Marked all 14 backlog features as `Status: BASELINED (2026-04-22)`.
- Wrote Rules + Examples + `@id` tags directly (no subagent delegation for bulk backlog work).
- Filed upstream issue on nullhack/temple8 to track the detection gap.

## Prevention

- Never call a PO subagent to process files in `backlog/` when `FLOW.md` state is `[IDLE]`.
- Ensure BASELINED gate is explicitly confirmed with the stakeholder before any Stage 2 work.
- Add a `[STEP-1-BACKLOG-CRITERIA]` state to the template so future projects do not hit this gap.
