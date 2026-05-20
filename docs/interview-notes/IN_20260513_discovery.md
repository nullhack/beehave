# IN_20260513_discovery — v3 Spec Synthesis

> **Status:** COMPLETE
> **Interviewer:** PO
> **Participant(s):** Stakeholder (via v3 specification document)
> **Session type:** Initial discovery

---

## General

| ID | Question | Answer |
|----|----------|--------|
| Q1 | Who are the users? | Python developers writing property-based tests who want Gherkin as the spec source of truth. |
| Q2 | What does the product do at a high level? | A CLI tool with three commands: `generate` (produces Hypothesis test stubs from Gherkin), `check` (verifies test bodies match feature specs via AST), and `clean` (removes unmapped test functions). |
| Q3 | Why does it exist — what problem does it solve? | Developers need Gherkin specifications to stay synchronized with test code without runtime coupling. Existing BDD tools inject frameworks into test code; beehave generates plain Hypothesis tests with zero imports from beehave itself. |
| Q4 | When and where is it used? | During development, at the command line. Developers run `generate` when writing features, `check` to verify consistency, and `clean` to remove stale tests. |
| Q5 | Success — what does "done" look like? | Generated stubs are valid Hypothesis tests. `check` reports zero violations. Unmapped functions are cleanly removed. No beehave imports appear in test code. |
| Q6 | Failure — what must never happen? | Partial output on failure. Tests must never import from beehave. Function name mapping must never be ambiguous (deterministic algorithm only). |
| Q7 | Out-of-scope — what are we explicitly not building? | Test runner, runtime framework, step-definition engine, assertion DSL, synonym resolver, Hypothesis replacement, bulk processor (one feature per invocation), `--dry-run` preview, code formatter/linter, cache/state manager. |

## Domain Questions

| ID | Question | Answer |
|----|----------|--------|
| Q8 | How does traceability work? | 1:1 via deterministic function naming: trim scenario name → collapse spaces → replace with `_` → prepend `test_`. E.g. `Scenario: deposit increases balance` → `test_deposit_increases_balance`. |
| Q9 | How are Background steps handled? | They merge into every scenario in scope transparently — no background functions, no special syntax. They appear as additional commented steps in the generated stub. |
| Q10 | How does `check` detect violations? | It re-parses features, AST-parses test files, joins by function name, and reports violations. Body enforcement checks for placeholder names and literal values. |
| Q11 | What is `clean`'s behavior when all functions are removed? | The file retains its import block. The file is never deleted. |
| Q12 | How does `check` report violations? | One line per violation in machine-parseable format: `<path>:<line>: <error_type>: <message>` to stdout. |
| Q13 | How does configuration work? | Via `pyproject.toml` under `[tool.beehave]`: features_dir, tests_dir, default_strategy, max_examples. |
| Q14 | How does `generate` handle idempotency? | Generate is idempotent — re-running produces the same output for unchanged features. |

---

## Quality Attributes

| ID | Attribute | Scenario | Target | Priority |
|----|-----------|----------|--------|----------|
| QA1 | Correctness | When `check` joins scenario to test by function name, the mapping is a deterministic bijection | 100% deterministic, no ambiguity | Must |
| QA2 | Reliability | When any command encounters an error, it reports immediately and exits non-zero | Zero partial output on failure | Must |
| QA3 | Simplicity | When tests are generated, they import only `hypothesis` — never `beehave` | Zero runtime coupling | Must |
| QA4 | Composability | When stable function APIs are consumed by future plugins, they remain backward-compatible | Public API documented and stable | Should |

---

## Pain Points Identified

- Existing BDD tools couple tests to frameworks at runtime, making tests fragile
- No existing tool enforces that test bodies stay consistent with Gherkin specs
- Unmapped test functions accumulate without automated cleanup

## Business Goals Identified

- Single source of truth: Gherkin features drive test generation
- Zero runtime coupling: tests are plain Hypothesis, no framework lock-in
- Automated consistency enforcement via `check` command

## Terms to Define (for glossary)

- stub — generated test function with commented steps and placeholder body
- unmapped — test function with no matching scenario in any feature file
- traceability — 1:1 mapping between scenario names and test function names
- body enforcement — AST-based check that test bodies are not placeholders
- idempotent — re-running `generate` produces identical output for unchanged input

## Action Items

- [x] Extract product definition from v3 spec
- [x] Extract interview notes from v3 spec
- [ ] Conduct domain discovery (event storming synthesis)
