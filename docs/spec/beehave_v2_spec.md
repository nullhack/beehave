# beehave v2 Specification

> A thin layer on Hypothesis for Gherkin-style BDD testing with vocabulary enforcement, automatic strategy inference, and 1:1 traceability.

---

## Core Concepts

### 1:1 Traceability

Every `Scenario` and `Scenario Outline` maps to exactly one test function. The mapping uses the scenario/outline title as the unique identifier.

**Titles must be globally unique across ALL features.** This is a deliberate departure from standard Gherkin (where titles only need to be unique within a Feature). The uniqueness constraint makes the title a reliable, human-readable ID — no `@id` tags needed.

**Title format rule:** Titles must contain only Unicode letters, digits, and spaces. No special characters (`@`, `-`, `'`, `/`, etc.). Titles must be non-empty after trimming whitespace — empty or whitespace-only titles are a parse error. The parser rejects invalid titles at parse time with a clear error message. Spaces are converted to underscores for the Python function name.

```
Scenario: spending reduces balance       →  def test_spending_reduces_balance(...)
Scenario Outline: specific transfers     →  def test_specific_transfers(...)
Scenario: 2nd login attempt              →  def test_2nd_login_attempt(...)
Scenario: connexion réussie              →  def test_connexion_réussie(...)
```

Rejected titles:
```
Scenario: user@admin creates hive        ❌  contains @
Scenario: hello-world                    ❌  contains -
Scenario: it's working                   ❌  contains '
```

If two features contain a `Scenario: login works`, or if two titles produce the same function name after space→underscore conversion and consecutive underscore collapsing, the parser raises a duplicate-title error.

### Step Decorators

`@Given`, `@When`, `@Then` decorate test functions. They serve two purposes:

1. **Vocabulary enforcement** — decorator text must match `.feature` step text
2. **Strategy binding** — `@Given` wraps Hypothesis `@given()`, wiring strategies to parameters

`@And` and `@But` are continuation decorators that inherit the step type of the immediately preceding `@Given`/`@When`/`@Then` on the same function. If `@And` or `@But` appears before any `@Given`/`@When`/`@Then` → collection-time error.

### Background

`@Background(func)` references a function decorated with step decorators. At collection time, background steps are prepended to the scenario's step list. `@And`/`@But` inheritance works across the combined (background + scenario) list.

```python
@Given("a user exists")
@And("the user has a wallet")
def background_wallet():
    ...

@Background(background_wallet)
@When("the user spends <amount>")
@Then("balance is reduced")
def test_spending(amount):
    ...
```

Rules:
1. `@Background(func)` — references a function decorated with step decorators
2. Background steps are prepended to the scenario's step list at collection time
3. `@And`/`@But` inherit from the immediately preceding `@Given`/`@When`/`@Then` in the combined list
4. Background function is NOT a test itself — not discovered by test runners
5. Multiple scenarios can share the same `@Background` function
6. Multiple `@Background` decorators on one test → collection-time error
7. Background with `<placeholders>` → placeholders are added to the scenario's parameter list

### Hypothesis Binding

`@Given` conditionally applies Hypothesis `@given()` only when placeholders exist in the step text:

- **Has `<placeholders>`** → `@Given` applies `@given(**strategies)`. Hypothesis manages value generation, shrinking, and test execution.
- **No placeholders across all steps** → no `@given()` wrapping. The function is a plain test — no Hypothesis involvement. Any test runner (pytest, unittest, etc.) that discovers `test_*` functions will pick it up.

No-param example:
```python
@Given("a hive is created")
@Then("we see 1 as output")
def test_default_hive():
    result = 1
    assert result == 1
```

With-param example:
```python
@Given("a user with balance <initial>")
@When("the user spends <amount>")
@Then("the balance should equal <remaining>")
def test_spending_reduces_balance(initial, amount, remaining):
    remaining = initial - amount
    assert remaining >= 0
```

---

### Decorator Resolution

beehave decorators are metadata collectors. They do not call Hypothesis directly.

At import time, beehave collects all decorators on a function in the order they appear in the feature file (Given → When → Then → And → But → Example), then wraps the function with the appropriate Hypothesis decorators:

1. Collect step text and placeholder metadata from `@Given`/`@When`/`@Then`/`@And`/`@But`
2. Infer strategies for each placeholder
3. Collect concrete values from `@Example` rows
4. Wrap with `@hypothesis.given(**strategies)` and `@hypothesis.example(**values)` in the correct Hypothesis stacking order

User-facing decorator order follows the feature file step order.

---

## Placeholder Syntax

Placeholder names must be valid Python identifiers and not Python keywords. The parser rejects invalid placeholder names (e.g., `<class>`, `<my name>`, `<count!>`) at parse time.

### `<name>` — variable placeholder

Appears in step text. Becomes a function parameter. Strategy auto-inferred.

```gherkin
Given a user with balance <initial>
```

```python
def test_...(initial):  # initial is a Hypothesis-generated value
```

### `'<name>'` — string-typed placeholder

Single-quoted forces `st.text()` strategy.

```gherkin
Given a bee named '<colony_name>'
```

```python
def test_...(colony_name):  # colony_name is st.text()
```

### Bare `<name>` — default strategy

Non-quoted defaults to the strategy configured in `default_strategy` (default: `st.integers()`). User can override by defining a module-level variable with the same name.

```python
# Override the default st.integers()
amount = st.decimals(min_value=Decimal("0"))
```

---

## Strategy Inference

Priority order (first match wins):

| Priority | Source | Strategy |
|----------|--------|----------|
| 1 | User-defined module variable | Whatever the user defined |
| 2 | Examples table column values | Inferred from values (see below) |
| 3 | `'<name>'` or `"<name>"` in step text | `st.text()` |
| 4 | Default (from `default_strategy` config) | `st.integers()` by default |

Examples table values have **higher precedence** than quoting convention. If `<name>` is bare in the step text but the Examples column contains `'My Name'`, the strategy is `st.text()` — the Examples table wins. If the Examples column type conflicts with the quoting convention (e.g., `'<name>'` quoted but Examples has integers), the Examples table wins but beehave emits a warning suggesting the user resolve the inconsistency.

### Examples table type inference

```gherkin
Examples:
  | initial | amount | rate  | name    |
  | 100     | 30.5   | 0.1   | Alice   |
  | 200     | 50.0   | 0.05  | Bob     |
```

**Primitive types:**

| Column values | Inferred type |
|---------------|--------------|
| `100`, `200` | `st.integers()` |
| `30.5`, `50.0` | `st.floats()` |
| `0.1`, `0.05` | `st.floats()` |
| `"Alice"`, `"Bob"` | `st.text()` |
| `true`, `false` | `st.booleans()` |

**Composite types:**

| Column values | Inferred type |
|---------------|--------------|
| `[1, 2, 3]` | `st.lists(st.integers())` |
| `["a", "b"]` | `st.lists(st.text())` |
| `{"a": 1}` | `st.dictionaries(st.text(), st.integers())` |
| `[1, "a"]` | Mixed — fall back to default, warn user to define manually |

Composite inner types are inferred from the actual values. If a column has mixed types across rows → fall back to `st.integers()` with a warning suggesting the user define the variable explicitly. Empty cells are treated as empty strings (`""`) — they infer as `st.text()`.

### User override

Define a module-level variable matching the placeholder name. The override takes priority over all inference. Module-level overrides apply to **all tests in the file**. If different strategies are needed for the same placeholder name, split the tests into separate files:

```python
from decimal import Decimal
from hypothesis import strategies as st

amount = st.decimals(min_value=Decimal("0"), max_value=Decimal("1000000"))
```

---

## Parameter Binding

**All placeholders from all steps (Given, When, Then) become `@given` params.**

This is a deliberate design choice for simplicity:
- One consistent rule — no Given/When/Then distinction for parameters
- All variables are accessible as function parameters
- Computed values (e.g. Then variables) are overridden by reassignment in the body

```gherkin
Scenario: spending reduces balance
  Given a user with balance <initial>
  When the user spends <amount>
  Then the balance should equal <remaining>
```

```python
@Given("a user with balance <initial>")
@When("the user spends <amount>")
@Then("the balance should equal <remaining>")
def test_spending_reduces_balance(initial, amount, remaining):
    remaining = initial - amount  # override generated remaining
    assert remaining >= 0
```

### Why all params, even Then variables?

1. **Simplicity** — one rule, no special cases
2. **Override in body** — reassign computed values; the generated value is discarded
3. **Avoids the `assume()` anti-pattern** — no need for `assume(remaining == initial - amount)`
4. **Scenario Outline examples** — all columns map naturally to params

### Scenario Outline + Examples

`Scenario Outline` requires at least one `Examples:` table with at least one data row. If missing → parse error. Multiple named `Examples:` tables are supported — all rows are merged into a single set, and each data row produces one `@Example` decorator on the test function. Table names are ignored.

```gherkin
Scenario Outline: spending with specific amounts
  Given a user with balance <initial>
  When the user spends <amount>
  Then the balance should equal <remaining>

  Examples:
    | initial | amount | remaining |
    | 100     | 30     | 70        |
    | 200     | 50     | 150       |
    | 50      | 25     | 25        |
```

```python
# User writes:
from beehave import Given, When, Then, Example

@Given("a user with balance <initial>")
@When("the user spends <amount>")
@Then("the balance should equal <remaining>")
@Example(initial=100, amount=30, remaining=70)
@Example(initial=200, amount=50, remaining=150)
@Example(initial=50, amount=25, remaining=25)
def test_spending_with_specific_amounts(initial, amount, remaining):
    remaining = initial - amount
    assert remaining == initial - amount

# Under the hood, beehave resolves to:
# @hypothesis.example(initial=100, amount=30, remaining=70)
# @hypothesis.example(initial=200, amount=50, remaining=150)
# @hypothesis.example(initial=50, amount=25, remaining=25)
# @hypothesis.given(initial=st.integers(), amount=st.integers(), remaining=st.integers())
# def test_spending_with_specific_amounts(initial, amount, remaining): ...
```

Each `@Example` row provides concrete values for all variables. Hypothesis runs the function once per Example with those exact values. `@Example` maps to Hypothesis `@example()` internally. `@Given` applies `@given()` with auto-inferred strategies.

In addition to the Example values, Hypothesis also generates random cases from the inferred strategies (standard Hypothesis behavior: `@example()` provides guaranteed cases, `@given()` adds random exploration). This catches edge cases beyond what the user specified.

**Configuration:** The number of random Hypothesis cases is configurable via `outline_random_examples` in `[tool.beehave]` (default: 1). Set to 0 to test only the Example rows with no random exploration.

```toml
[tool.beehave]
outline_random_examples = 1   # 0 = Example-only, N = N random cases beyond Examples
```

---

## Body Enforcement

At test collection time, beehave validates the test function body. For Scenario Outline, enforcement checks the shared function body once — not per-Example execution.

### 1. All placeholders must appear in the body

Every `<variable>` from the Gherkin steps must be referenced somewhere in the function body. Enforcement uses AST analysis — only actual code references count, not comments or string literals.

```gherkin
Then the balance should equal <remaining>
```

```python
def test_...(initial, amount, remaining):
    remaining = initial - amount  # ✓ remaining appears
```

If `remaining` never appears → collection-time warning or error.

### 2. Literal values must appear in the body

Numbers (digit sequences) and quoted strings in step text must appear in the test body. Matching is whole-word: numeric literals use `\b` word boundaries, string literals match exactly.

```gherkin
Given a hive with 3 bees
Then the honey is "golden"
```

```python
def test_...():
    bee_count = 3         # ✓ literal 3 appears (whole-word match)
    assert honey == "golden"  # ✓ literal "golden" appears
```

Symbols attached to numbers (e.g., `1%`) are not numeric literals — the user must quote them (`'1%'`) to enforce as a string literal.

This ensures the Gherkin documents behavior that the test actually verifies.

---

## Vocabulary Enforcement

### Cache File

beehave maintains a cache file (`.beehave/cache.json`) built on `sync`/`generate` from `.feature` files. The cache is updated when `.feature` files change (compared by edit time). Storing the cache avoids re-parsing all feature files on every test collection.

**Cache structure per scenario:**
- `title` → derived function name
- `steps`: ordered list of step text hashes (background steps + scenario steps, in Gherkin order)
- `examples`: ordered list of value maps for Scenario Outline (matched by exact values)

### Collection-Time Check

At test collection time, beehave validates each test function against the cache:

1. **Resolve function** — map scenario title to test function name. If no function exists → missing test (not a vocabulary error, handled by `clean` command)
2. **Collect beehave decorators** — gather only `@Given`/`@When`/`@Then`/`@And`/`@But` decorators from the test function, in decorator order. Non-beehave decorators (e.g., `@pytest.mark.skip`) are ignored.
3. **Resolve background** — if `@Background(func)` is present, prepend the background function's beehave step decorators to the test's step decorators → combined ordered list
4. **Hash step text** — hash each step text in the combined list
5. **1:1 ordered match** — compare against cached step hashes. Same count, same order, same hashes.
6. **Scenario Outline** — `@Example` rows matched 1:1 by exact values against cached examples

Matching is on the template form — placeholder syntax `<name>` is compared literally, not resolved to values. Matching is case-sensitive and exact.

### Error Examples

- "Scenario 'abc' expects 3 steps, test has 2 beehave step decorators"
- "Step 2 mismatch: expected 'When the user spends <amount>', got 'When the user deposits <amount>'"
- "Scenario 'abc' expects 2 Example rows, test has 1"

### Fix Command

`fix(name)` aligns decorator text with `.feature` step text using the cache. Detects drift by comparing hashes, updates decorator strings to match.

### Clean Command

`clean(name)` removes orphan test functions (no matching scenario in cache) and reports missing test functions (scenario in cache but no matching test).

---

## CLI Commands

| Command | Purpose |
|---------|---------|
| `generate(name)` | Create test stubs from `.feature` files |
| `fix(name)` | Align decorator text with `.feature` step text |
| `clean(name)` | Remove orphan test functions |

### generate

Reads `.feature` files from `docs/features/`. Updates `.beehave/cache.json`. For each scenario without a matching test function:

1. Derive function name from scenario title
2. Collect all `<placeholder>` from all steps
3. Infer strategies (user override > Examples table > quoting > default)
4. Generate stub with decorators, params, and commented strategy hints

Generated stub:

```python
from beehave import Given, When, Then, Example
from hypothesis import strategies as st

# initial = st.integers()  # Override if needed
# amount = st.integers()   # Override if needed
# remaining = st.integers()  # Override if needed

@Given("a user with balance <initial>")
@When("the user spends <amount>")
@Then("the balance should equal <remaining>")
def test_spending_reduces_balance(initial, amount, remaining):
    remaining = initial - amount
    assert remaining >= 0
```

---

## File Conventions

```
docs/features/<feature_name>.feature     # Gherkin feature files
tests/features/<feature_name>/default_test.py  # Generated test stubs
```

---

## Architecture

### `beehave.decorators`

- `@Given(step_text)` — wraps Hypothesis `@given()`, applies strategies for all placeholders
- `@When(step_text)` — attaches step metadata, vocabulary check
- `@Then(step_text)` — attaches step metadata, vocabulary check
- `@And(step_text)` — continuation, inherits preceding step type
- `@But(step_text)` — continuation, inherits preceding step type
- `@Example(**kwargs)` — provides concrete values for Scenario Outline rows. Keys must match placeholder names exactly — unknown or missing keys → collection-time error
- `@Background(func)` — injects background step decorators before scenario steps

### `beehave.traceability`

- Parse `.feature` files
- Extract scenarios, placeholders, Examples tables
- Derive function names from scenario titles
- Infer types from quoting and Examples columns

### `beehave.validation`

- Collection-time vocabulary enforcement
- Global title uniqueness check — no two scenarios/outlines may share a title across all features
- Body enforcement: verify placeholders and literals appear
- Orphan detection: test functions with no matching scenario, scenarios with no test function

### `beehave.cli`

- `generate`, `fix`, `clean` commands
- Stub generation with strategy inference

---

## Gherkin Extensions and Constraints

beehave extends and constrains standard Gherkin. These are the deliberate deviations:

### Extensions (beehave adds to Gherkin)

| Feature | Standard Gherkin | beehave |
|---------|-----------------|---------|
| `<placeholder>` in steps | Only in Scenario Outline steps | Allowed in any step (Given/When/Then/And/But) |
| `'<placeholder>'` syntax | N/A | Single-quoted forces `st.text()` strategy |
| Examples table type inference | N/A | Column values infer strategy types (int/float/text/bool/list/dict) |
| Examples precedence | N/A | Examples table type overrides quoting convention |

### Constraints (beehave restricts Gherkin)

| Constraint | Standard Gherkin | beehave |
|-----------|-----------------|---------|
| Title uniqueness | Unique within a Feature | Globally unique across ALL features |
| Title characters | Any text | Unicode letters, digits, and spaces only |
| `@id` tags | User-defined tags | Not used — titles serve as identifiers |

### Body enforcement (test-side constraints)

- All `<variables>` from Gherkin steps must appear in the test function body
- Literal numbers and quoted strings in step text must appear in the test function body

---

## Configuration

beehave reads settings from `[tool.beehave]` in `pyproject.toml`:

```toml
[tool.beehave]
default_strategy = "integers"   # integers | floats | text | booleans
auto_inference = true           # false = strategy inference disabled, user must define all strategies; Examples values still read for @Example
features_dir = "docs/features"  # where .feature files live
tests_dir = "tests/features"    # where generated test files go
outline_random_examples = 1     # 0 = Example-only, N = N random Hypothesis cases beyond Examples
```

| Setting | Values | Default | Effect |
|---------|--------|---------|--------|
| `default_strategy` | `"integers"`, `"floats"`, `"text"`, `"booleans"` | `"integers"` | Strategy used when no other inference applies (priority 4) |
| `auto_inference` | `true`, `false` | `true` | If `false`, every `<variable>` must be manually defined at module level. Strategy inference from quoting convention and Examples table types is disabled. However, Examples table values are still read to generate `@Example` concrete values — they just don't infer strategies. Parser errors on undefined strategy vars. |
| `features_dir` | any path | `"docs/features"` | Where beehave looks for `.feature` files |
| `tests_dir` | any path | `"tests/features"` | Where beehave generates test stubs |
| `outline_random_examples` | any non-negative integer | `1` | Number of random Hypothesis cases generated beyond `@Example` rows for Scenario Outline. 0 = Example-only, no random exploration |

String detection auto-detects both `'` and `"` as quote characters. No configuration needed — if a `<placeholder>` is wrapped in matching quotes of either type, it is treated as `st.text()`.

---

## What beehave IS NOT

- Does NOT provide an assertion DSL — use Python `assert`
- Does NOT execute step definitions — the test body is plain Python
- Does NOT replace Hypothesis — composes with it
- Does NOT do NLP or synonym resolution — vocabulary is exact matching
- Does NOT require pytest for core functionality — vocabulary enforcement and decorator metadata are runner-agnostic. Hypothesis is only applied when placeholders are present. No-param tests are plain functions discoverable by any test runner.

---

## Examples

### Plain scenario with auto-inferred strategies

```gherkin
Feature: Hive management

  Scenario: bee count after birth
    Given a hive with <bee_count> bees
    When <new_bees> bees are born
    Then the total is <bee_count> plus <new_bees>
```

```python
from beehave import Given, When, Then

@Given("a hive with <bee_count> bees")
@When("<new_bees> bees are born")
@Then("the total is <bee_count> plus <new_bees>")
def test_bee_count_after_birth(bee_count, new_bees):
    total = bee_count + new_bees
    assert total == bee_count + new_bees
```

### String-typed placeholder

```gherkin
  Scenario: bee has a name
    Given a bee named '<name>'
    Then the bee responds to '<name>'
```

```python
@Given("a bee named '<name>'")
@Then("the bee responds to '<name>'")
def test_bee_has_a_name(name):
    assert len(name) > 0
```

### User override with constrained strategy

```gherkin
  Scenario: balance never negative
    Given a user with balance <initial>
    When the user spends <amount>
    Then the balance is not negative
```

```python
from hypothesis import strategies as st

initial = st.integers(min_value=0)
amount = st.integers(min_value=0)

@Given("a user with balance <initial>")
@When("the user spends <amount>")
@Then("the balance is not negative")
def test_balance_never_negative(initial, amount):
    remaining = initial - amount
    assert remaining >= 0
```

### Scenario Outline with Examples

```gherkin
  Scenario Outline: specific transfers
    Given account A has <balance_a>
    And account B has <balance_b>
    When <transfer> is moved from A to B
    Then A has <result_a> and B has <result_b>

    Examples:
      | balance_a | balance_b | transfer | result_a | result_b |
      | 100       | 50        | 30       | 70       | 80       |
      | 200       | 0         | 50       | 150      | 50       |
```

```python
from beehave import Given, When, Then, And, Example

@Given("account A has <balance_a>")
@And("account B has <balance_b>")
@When("<transfer> is moved from A to B")
@Then("A has <result_a> and B has <result_b>")
@Example(balance_a=100, balance_b=50, transfer=30, result_a=70, result_b=80)
@Example(balance_a=200, balance_b=0, transfer=50, result_a=150, result_b=50)
def test_specific_transfers(balance_a, balance_b, transfer, result_a, result_b):
    result_a = balance_a - transfer
    result_b = balance_b + transfer
    assert result_a >= 0
    assert result_b >= 0
```
