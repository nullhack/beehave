# Glossary: beehave

> Living glossary of domain terms used in this project.
> Written and maintained by the Domain Expert during Discovery.
> Append-only: never edit or remove past entries. If a term changes, mark it retired in favor of the new entry and write a new entry.
> Code and tests take precedence over this glossary — if they diverge, refactor the code, not this file.

---

## Entry Format

```
## <Term>

**Definition:** <one sentence — genus + differentia: "A [category] that [distinguishes it from others in that category]">

**Aliases:** <deprecated synonyms the team should stop using, or "none">

**Example:** <one sentence showing the term in use in this project; optional but encouraged>

**Source:** <feature stem or discovery session date>
```

Entries are sorted alphabetically.

---

## Background

**Definition:** A Gherkin block of shared steps that are transparently merged into every scenario in its containing feature, with no placeholders allowed. Both numeric and quoted-string literals are enforced by default; configurable via `background_check_numeric` and `background_check_string` in pyproject.toml.

**Aliases:** none

**Example:** A `Background:` block with `Given a user is logged in` prepends that step to all scenarios in the feature.

**Source:** 2026-05-13

---

## Bijection

**Definition:** A one-to-one correspondence between the example rows in a Scenario Outline's Examples table and the `@example()` decorated test functions in the matching test file.

**Aliases:** examples bijection

**Example:** A Scenario Outline with 3 example rows produces one test function with exactly 3 `@example()` decorators — no more, no fewer.

**Source:** 2026-05-13

---

## Body Enforcement

**Definition:** An AST-level check that every placeholder in a scenario step appears as a `Name` node and every literal appears as a `Constant` node in the corresponding test function body.

**Aliases:** body check, enforcement

**Example:** If a step contains `<count>` and `"hello"`, the test body must reference a variable `count` and contain the string constant `"hello"`.

**Source:** 2026-05-13

---

## Examples Table

**Definition:** A Gherkin data table associated with a Scenario Outline that provides concrete parameter values for each example row, with optional type inference from cell values.

**Aliases:** Examples

**Example:** An Examples table with columns `| count | name |` and rows `| 3 | "Alice" |` provides values for the `<count>` and `<name>` placeholders.

**Source:** 2026-05-13

---

## Feature

**Definition:** A Gherkin source file (`.feature`) containing a globally-unique title, an optional Background, Rules, Scenarios, and Scenario Outlines that serves as the root aggregate for parsing and determines the test directory structure.

**Aliases:** Feature File

**Example:** `docs/features/cart/add_item.feature` with title "Add item to cart" maps to `tests/features/cart/add_item/default_test.py`.

**Source:** 2026-05-13

---

## Function Name

**Definition:** The sole lookup key for matching scenarios to test functions, derived deterministically from a scenario title by trimming whitespace, collapsing internal spaces to underscores, and prepending `test_`.

**Aliases:** derived name, test name

**Example:** Scenario title `"Add item when cart is empty"` becomes function name `test_add_item_when_cart_is_empty`.

**Source:** 2026-05-13

---

## Import Block

**Definition:** The section of a Python test file containing import statements that must be preserved when unmapped functions are cleaned from the file.

**Aliases:** imports, import section

**Example:** `from hypothesis import given, example, strategies as st` at the top of a generated test file.

**Source:** 2026-05-13

---

## Literal

**Definition:** A value extracted from step text — either a sequence of numeric digits or a double-quoted string — that must appear as an AST `Constant` node in the matching test function body.

**Aliases:** literal value

**Example:** In step `Given 3 items with name "Alice"`, the literals are `3` (numeric) and `"Alice"` (quoted string).

**Source:** 2026-05-13

---

## Module-Level Strategy

**Definition:** A Python variable defined at module scope in a test file whose name matches a placeholder and whose value is a Hypothesis strategy, taking highest priority during strategy resolution.

**Aliases:** module strategy, strategy variable

**Example:** `count_strategy = st.integers(min_value=0, max_value=100)` resolves the `<count>` placeholder without needing a default.

**Source:** 2026-05-13

---

## Unmapped

**Definition:** A test function with no matching scenario in any feature file, or a scenario with no matching test function in the expected test file.

**Aliases:** unmapped function, unmapped scenario

**Example:** A function `test_old_behavior` remaining after the corresponding scenario was deleted from the feature file.

**Source:** 2026-05-13

---

## Placeholder

**Definition:** A `<name>` token in Gherkin step text that represents a parameterized value and becomes a Hypothesis `@given()` parameter in the generated test function.

**Aliases:** template variable, parameter

**Example:** In step `Given <count> items`, the placeholder `<count>` generates a `@given(count=...)` decorator.

**Source:** 2026-05-13

---

## Rule

**Definition:** A named organizational block within a Gherkin Feature that groups related scenarios, with a title that must be unique within its parent feature.

**Aliases:** none

**Example:** `Rule: Cart total calculation` grouping scenarios about cart arithmetic.

**Source:** 2026-05-13

---

## Scenario

**Definition:** A single test case defined by a title and an ordered sequence of Given/When/Then steps, mapped 1:1 to a test function via deterministic name derivation.

**Aliases:** test scenario

**Example:** `Scenario: Add item to empty cart` with steps `Given an empty cart` / `When I add an item` / `Then the cart has one item`.

**Source:** 2026-05-13

---

## Scenario Outline

**Definition:** A parameterized scenario template combined with an Examples table that generates a single test function decorated with one `@example()` per table row.

**Aliases:** Scenario Template, Outline

**Example:** A Scenario Outline with `<count>` in a step and 3 example rows produces one test function with 3 `@example()` decorators.

**Source:** 2026-05-13

---

## Step

**Definition:** A single Given, When, or Then line in a Gherkin scenario that may contain placeholders and literals, forming the basis for body enforcement checks.

**Aliases:** step line, scenario step

**Example:** `Given <count> items with name "Alice"` contains one placeholder (`<count>`) and two literals (`"Alice"` and potentially `count`'s resolved value).

**Source:** 2026-05-13

---

## Strategy

**Definition:** A Hypothesis strategy that determines how placeholder values are generated, resolved by checking (1) module-level variable, (2) Examples table type inference, (3) default configuration, in priority order.

**Aliases:** Hypothesis strategy, generation strategy

**Example:** The placeholder `<count>` resolves to `st.integers()` by default unless a module-level `count_strategy` variable or an Examples table column type overrides it.

**Source:** 2026-05-13

---

## Stub

**Definition:** A generated test function with a body containing only `...` (Ellipsis) or `pass`, which is exempt from all body enforcement checks.

**Aliases:** test stub, generated stub

**Example:** `def test_add_item_to_empty_cart(): ...` is generated for a scenario with no existing matching function.

**Source:** 2026-05-13

---

## Type Inference

**Definition:** The process of determining a Hypothesis strategy by analyzing the values in an Examples table column, used as a fallback when no module-level strategy exists.

**Aliases:** Examples table type inference

**Example:** An Examples column containing `1`, `5`, `10` infers an integer strategy; a column containing `"Alice"`, `"Bob"` infers a string strategy.

**Source:** 2026-05-13
