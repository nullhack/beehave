# ADR: FrameworkAdapter as a structural Protocol

| Field | Value |
|-------|-------|
| **Date** | 2026-04-22 |
| **Feature** | adapter-contract, pytest-adapter |
| **Status** | Accepted |

## Context

**Question (D2):** Should `FrameworkAdapter` be a `typing.Protocol` or an ABC?

Structural protocols allow third-party adapters to satisfy the interface without importing from `beehave`. An ABC forces a hard import coupling. pyright enforces Protocol conformance statically with zero runtime overhead. The stakeholder confirmed zero import coupling as a design goal.

---

## Decision

`FrameworkAdapter` is defined as a `typing.Protocol` (structural subtyping), not an abstract base class.

## Reason

Structural protocols allow third-party adapters to satisfy the interface without importing from `beehave`, keeping the dependency graph clean and enabling duck-typed adapters in future without a registration mechanism.

## Alternatives Considered

- **ABC (abstract base class)**: rejected — forces third-party adapters to import `beehave`; creates a hard coupling; adds no runtime safety benefit over Protocol + pyright
- **Plugin entry points (importlib.metadata)**: rejected — out of v1 scope; over-engineered for a single built-in adapter; can be layered on top of Protocol later

## Consequences

- (+) Third-party adapters need zero beehave imports to satisfy the contract
- (+) pyright enforces the Protocol at type-check time with zero runtime overhead
- (+) Easy to extend to entry-point registration in v2 without breaking existing adapters
- (-) Runtime errors if an adapter is missing a method (no ABC `__abstractmethods__` guard); mitigated by pyright
