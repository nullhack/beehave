# ADR: Performance targets and cache role

| Field | Value |
|-------|-------|
| **Date** | 2026-04-22 |
| **Feature** | cache-management, id-generation |
| **Status** | Accepted |

## Decision

The target scale is **medium** (100–1,000 Examples per project). A full scan of all `.feature` files on every run is acceptable at this scale. The cache is a **performance optimisation**, not a load-bearing architectural requirement — sync must be correct without it; the cache only speeds it up.

## Reason

Stakeholder confirmed medium scale as the design target. At 1,000 Examples across ~100 files, a full scan completes in well under 1 second on any modern filesystem. The cache adds complexity; making it optional-for-correctness keeps the system simpler and the cache failure modes safe (rebuild = fall back to full scan).

## Alternatives Considered

- **Cache as load-bearing (required for correct operation)**: rejected — adds hard dependency on cache coherence; full scan is fast enough at target scale
- **No cache at all**: considered — acceptable for v1 correctness but rejected because the cache is already designed into the domain model and provides real user value (incremental sync feedback)
- **Large-scale design (10k+ Examples)**: out of scope for v1; if scale grows, the cache can be promoted to load-bearing without breaking the API

## Consequences

- (+) Cache failure never blocks sync — silently rebuild and proceed
- (+) Full scan is the correctness baseline; cache is an optimisation layer on top
- (+) Simplifies cache-management implementation: stale/corrupt cache → rebuild, not error
- (-) At >1,000 Examples, full-scan fallback may be slow; acceptable for v1 but a known scaling limit
- (-) Gap A2 is now resolved: no sub-second SLA enforced; correctness over speed
