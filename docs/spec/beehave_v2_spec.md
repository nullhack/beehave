# beehave v2 Specification

> A thin layer on Hypothesis for Gherkin-style BDD testing with vocabulary enforcement, automatic strategy inference, and 1:1 traceability.

---

## Core Concepts

### 1:1 Traceability

Every `Scenario` and `Scenario Outline` maps to exactly one test function. The mapping uses the scenario/outline title as the unique identifier.

**Titles must be globally unique across ALL features.** This is a deliberate departure from standard Gherkin (where titles only need to be unique within a Feature). The uniqueness constraint makes the title a reliable, human-readable ID — no `@id` tags needed.

**Title format rule:** Scenario and Scenario Outline titles must contain only Unicode letters, digits, and spaces. No special characters (`@`, `-`, `'`, `/`, etc.). Titles must be non-empty after trimming whitespace — empty or whitespace-only titles are a parse error. The parser rejects invalid titles at parse time with a clear error message. Spaces are converted to underscores for the Python function name. **Feature and Rule titles follow the same character restriction** — Unicode letters, digits, and spaces only — to ensure background function names derived from them are valid Python identifiers.

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
2. **Strategy binding** — the decorator resolution phase applies Hypothesis `@given()` when ANY step across all decorators contains `<placeholders>`, wiring strategies to parameters

All step decorators (`@Given`, `@When`, `@Then`) are metadata collectors. No single decorator type is responsible for triggering Hypothesis wiring — strategy resolution fires once per function after all step decorators have been collected, triggered by the presence of placeholders in any step text.

Multiple decorators of the same type are allowed on a single function (e.g., two `@Given` decorators). This maps to multiple Given steps in the Gherkin. Vocabulary enforcement matches by position as usual.

`@And` and `@But` are continuation decorators that inherit the step type of the immediately preceding `@Given`/`@When`/`@Then` in the combined step list (background + scenario). If `@And` or `@But` appears before any `@Given`/`@When`/`@Then` in the combined list → collection-time error.

### Background

Gherkin `Background:` sections in `.feature` files define shared setup steps for all scenarios in their scope. In Python, `@Background(func)` references a function whose step decorators are vocabulary-verified against the cached background steps.

**Feature-level background** applies to all scenarios in the feature. **Rule-level background** (inside a `Rule:` block) applies to scenarios within that rule. When both exist, backgrounds compose: feature background steps run first, then rule background steps, then scenario steps.

```gherkin
Feature: Bank

  Background:
    Given a user exists
    And the user is authenticated

  Rule: transfer rules
    Background:
      Given the account is open

    Scenario Outline: transfers
      When <amount> is transferred
      Then balance is <result>

      Examples:
        | amount | result |
        | 10     | 90     |
        | 20     | 80     |
```

```python
@Given("a user exists")
@And("the user is authenticated")
def background_bank():
    ...

@Given("the account is open")
def background_transfer_rules():
    ...

@Background(background_bank)
@Background(background_transfer_rules)
@When("<amount> is transferred")
@Then("balance is <result>")
@Example(amount=10, result=90)
@Example(amount=20, result=80)
def test_transfers(amount, result):
    ...
```

Rules:
1. `Background:` in `.feature` files is parsed and stored in the cache (feature-level or rule-level)
2. `@Background(func)` in Python references a function decorated with step decorators. The function must start with a `@Given`, `@When`, or `@Then` (not `@And`/`@But`), consistent with Gherkin's requirement that Background steps begin with Given/When/Then.
3. At collection time, `@Background(func)` step decorators are verified against cached background steps (same hash-based 1:1 matching as scenario steps)
4. Backgrounds compose: feature background + rule background (if present) + scenario steps
5. The number of `@Background` decorators must match the number of `Background:` sections in the feature/rule hierarchy — mismatch → collection-time error. Multiple `@Background` decorators must be in hierarchical order: feature background first, rule background second. Reversed order → collection-time error.
6. `@And`/`@But` inherit from the immediately preceding `@Given`/`@When`/`@Then` in the combined list
7. Background function is NOT a test itself — not discovered by test runners (don't name it `test_*`)
8. Multiple scenarios can share the same `@Background` function
9. **No `<placeholders>` in Background.** Background steps must be fixed (literal) text — no `<name>` parameterization. This aligns with standard Gherkin, which does not support placeholders in Background. Parameterized setup should use plain `Scenario` with `@Given` steps containing `<placeholders>`.
10. A feature or rule may have at most one `Background:` section. Multiple → parse error
11. Rule titles must be unique within a Feature. Duplicate rule titles → parse error.

### Hypothesis Binding

The decorator resolution phase conditionally applies Hypothesis `@given()` when placeholders exist in any step text across all decorators:

- **Has `<placeholders>`** in any step → decorator resolution applies `@given(**strategies)`. Hypothesis manages value generation, shrinking, and test execution. The `max_examples` config controls `hypothesis.settings(max_examples)` for all scenarios with `<placeholders>`: for Scenario Outline, `@Example` rows always run and `max_examples` adds N random cases beyond them; for plain scenarios, N random cases total. Default: 1 (configurable via `max_examples` in `[tool.beehave]`).
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

At import time, beehave collects all decorators on a function in **Gherkin order** as written by `generate` (Given → When → Then → And → But → Example). The hash sequence in the cache defines the canonical ordering. Vocabulary enforcement matches decorator hashes against cached hashes positionally — **do not reorder step decorators.** Then wraps the function with the appropriate Hypothesis decorators:

1. Collect step text and placeholder metadata from `@Given`/`@When`/`@Then`/`@And`/`@But`
2. If ANY step contains `<placeholders>` → infer strategies for each placeholder and wrap with `@hypothesis.given(**strategies)`. This is independent of which step type (`@Given`, `@When`, `@Then`) contains the placeholders.
3. Collect concrete values from `@Example` rows
4. Wrap with `@hypothesis.example(**values)` outside `@hypothesis.given()` — `@example()` outermost, `@given()` innermost (Hypothesis requirement)

User-facing decorator order follows the feature file step order.

---

## Placeholder Syntax

Placeholder names must be valid Python identifiers, not Python keywords, and not Python builtins (names in the `builtins` module, e.g., `list`, `dict`, `str`, `len`, `print`). The parser rejects invalid placeholder names at parse time.

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
| `true`, `True`, `TRUE`, `false`, `False`, `FALSE` | `st.booleans()` (case-insensitive) |

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

When `@Example` rows are generated for Scenario Outline, each row includes values for **all** placeholders from the scenario's own steps. This ensures `@Example` always has values for every parameter, satisfying Hypothesis's requirement that `@example()` specify every parameter present in `@given()`.

### Scenario Outline + Examples

`Scenario Outline` requires at least one `Examples:` table with at least one data row. If missing → parse error. Every scenario (plain or outline) must have at least one step — stepless scenarios are a parse error. Multiple named `Examples:` tables are supported — all rows are merged into a single set, and each data row produces one `@Example` decorator on the test function. Table names are ignored. All `Examples:` tables within a single Scenario Outline must have **identical column headers** (same names, same order). If column headers differ between tables → parse error indicating which tables are inconsistent and their column sets. **Column headers must cover ALL placeholders from the scenario's step list.** Missing columns → parse error listing the missing placeholder names. **Unreferenced columns** (an Examples column with no matching `<placeholder>` in any step) → parse error: "Examples column 'X' has no matching `<X>` in any step."

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

Each `@Example` row provides concrete values for all variables. Hypothesis runs the function once per Example with those exact values. `@Example` maps to Hypothesis `@example()` internally. The decorator resolution phase applies `@given()` with auto-inferred strategies when placeholders are present.

In addition to the Example values, Hypothesis also generates random cases from the inferred strategies (standard Hypothesis behavior: `@example()` provides guaranteed cases, `@given()` adds random exploration). This catches edge cases beyond what the user specified.

**Configuration:** The number of random Hypothesis cases is configurable via `max_examples` in `[tool.beehave]` (default: 1). Applies to all scenarios with `<placeholders>`. For Scenario Outline, `@Example` rows always run regardless of this setting. Set to 0 to disable random exploration (Scenario Outline: only `@Example` rows run).

```toml
[tool.beehave]
max_examples = 1   # 0 = no random cases, N = N random Hypothesis cases
```

---

## Body Enforcement

At test collection time (i.e., at test discovery/setup time, before test execution), beehave validates the test function body. For Scenario Outline, enforcement checks the shared function body once — not per-Example execution.

**Stub exemption:** Functions whose body is only `...` (Ellipsis — a single AST `Expr(Constant(value=Ellipsis))` node) are exempt from body enforcement. This allows `generate` to create stubs without triggering enforcement. Once the user replaces `...` with real code, enforcement activates.

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

beehave maintains a cache file (`.beehave/cache.json`) built on `generate` from `.feature` files. The cache is a pure derived artifact — it contains nothing that can't be reconstructed from `.feature` files. Add `.beehave/` to `.gitignore`. All paths in the cache and in `features_dir`/`tests_dir` config are relative to the project root (the directory containing `pyproject.toml`).

**Staleness detection:** SHA-256 content hashing (not file edit time). Content hashing is immune to clock issues, git operations, `touch`, and NFS/CI filesystem quirks. Feature files are small (<50KB total), so hashing costs <1ms.

**Cache structure:**
```json
{
  "version": 1,
  "features": {
    "docs/features/shopping.feature": {
      "content_hash": "a1b2c3d4...",
      "background": {
        "steps": [
          {"keyword": "Given", "text": "a user exists"},
          {"keyword": "And", "text": "the user is authenticated"}
        ]
      },
      "rules": {
        "transfer rules": {
          "background": {
            "steps": [
              {"keyword": "Given", "text": "the account is open"}
            ]
          },
          "scenarios": {}
        }
      },
      "scenarios": {
        "spending reduces balance": {
          "function_name": "test_spending_reduces_balance",
          "steps": [
            {"keyword": "Given", "text": "a user with balance <initial>"},
            {"keyword": "When", "text": "the user spends <amount>"},
            {"keyword": "Then", "text": "the balance should equal <remaining>"}
          ],
          "placeholders": ["initial", "amount", "remaining"],
          "examples": []
        }
      }
    }
  }
}
```

`function_name` is computed at cache build time: title → spaces to underscores → collapse consecutive underscores → prepend `test_`. This enables O(n) lookup without lossy reverse-mapping.

The `examples` field stores a list of dicts with **typed values** (coerced at parse time using the same type inference rules as strategy inference: `"100"` → `100`, `"0.1"` → `0.1`, `"Alice"` → `"Alice"`, `"true"` → `True`). For plain scenarios, `examples` is `[]`. For Scenario Outlines:

```json
"examples": [
  {"amount": 100, "result": 90},
  {"amount": 200, "result": 80}
]
```

A feature without a `Background:` section has no `background` key. A rule without a `Background:` section has no `background` key in its rule entry.

**Cache scope:** Feature files only. Test files are developer-owned and parsed directly — never cached.

**Cache lifecycle:**
- **Missing cache** → silent rebuild on next operation. No error, no warning.
- **Feature file changed** (content hash mismatch) → rebuild that file's entry.
- **Feature file deleted** → remove stale entry. Tests referencing those scenarios become orphans.
- **Feature file renamed** → treated as deletion + addition. Old entry dropped, new entry parsed.
- **New feature file** → detected during validation, parsed and added.
- **Test file edited** → cache unaffected (cache only tracks feature files).

**Every operation validates the cache first** — no operation ever uses stale data. Validation is incremental: only changed/new files trigger parsing.

**Rebuild triggers:**

| Operation | Cache behavior |
|-----------|---------------|
| `generate` | Validate → rebuild stale/new → generate stubs → write cache |
| `fix` | Validate → rebuild stale/new → align decorators |
| `clean` | Validate → rebuild stale/new → detect orphans |
| Test collection | Validate → rebuild stale/new → enforce vocabulary |

### Collection-Time Check

At test collection time (i.e., at test discovery/setup time, before test execution), beehave validates each test function against the cache:

1. **Resolve function** — scan cache entries (feature-level `scenarios` first, then each rule's `scenarios`) for a scenario whose `function_name` matches the test function name. If no match → missing test (not a vocabulary error, handled by `clean` command)
2. **Collect beehave decorators** — gather only `@Given`/`@When`/`@Then`/`@And`/`@But` decorators from the test function, in Gherkin order. Non-beehave decorators (e.g., `@pytest.mark.skip`) are ignored.
3. **Resolve backgrounds** — determine how many `Background:` sections exist in the feature/rule hierarchy for this scenario. The test must have the same number of `@Background(func)` decorators. For each `@Background` decorator, verify its step decorator hashes against the cached background step hashes (feature background first, then rule background). Prepend background step hashes to scenario step hashes → full expected hash list. Prepend `@Background` decorator hashes to test step decorator hashes → full actual hash list. `@And`/`@But` inheritance is checked on the combined list — a scenario starting with `@And` is valid if a background step precedes it in the combined list.
4. **Hash step text** — hash each step text in the combined list
5. **1:1 ordered match** — compare hashes against the cached step hashes (computed from the stored step text). Same count, same order, same hashes.
6. **Scenario Outline** — `@Example` rows matched by **deep equality bijection** against cached examples. For each cached example row, find a matching `@Example` decorator using `==` (supports composite types like lists/dicts). Every cached row must have exactly one match, and every `@Example` must match exactly one cached row. Order of rows does not matter. `@Example` values must match the inferred type exactly — lists in Gherkin remain lists in Python, not tuples.

Matching is on the template form — placeholder syntax `<name>` is compared literally, not resolved to values. Matching is case-sensitive and exact, with one exception: **quote normalization for string-typed placeholders.** Both `'<name>'` and `"<name>"` are treated as equivalent template forms — quote characters surrounding a `<placeholder>` are normalized before comparison. All other text is compared exactly.

### Error Examples

- "Scenario 'abc' expects 3 steps, test has 2 beehave step decorators"
- "Step 2 mismatch: expected 'When the user spends <amount>', got 'When the user deposits <amount>'"
- "Scenario 'abc' expects 2 Example rows, test has 1"

### Fix Command

`fix(name)` aligns decorator text with `.feature` step text using the cache. Detects drift by comparing hashes, updates decorator strings to match. **Fix updates decorator text in scope** — it updates both test function step decorators AND `@Background` function step decorators when the corresponding `.feature` content changes. Fix does not modify function signatures, parameters, bodies, or imports. Adding or removing parameters is the user's responsibility. Two layers of detection catch mismatches: Python `TypeError` at import time if `@given()` provides a param the function doesn't accept, and body enforcement if a placeholder isn't referenced.

### Clean Command

`clean(name)` removes orphan test functions (no matching scenario in cache) and reports missing test functions (scenario in cache but no matching test). Additionally, **clean detects orphan parameters** — function signature parameters that don't appear in any `@given()` decorator kwargs. These indicate a `<placeholder>` was removed from the feature but the parameter wasn't cleaned up manually. **Clean also removes background functions** that are no longer referenced by any `@Background` decorator in the same file.

---

## CLI Commands

| Command | Purpose |
|---------|---------|
| `generate(name)` | Create test stubs from `.feature` files |
| `fix(name)` | Align decorator text with `.feature` step text |
| `clean(name)` | Remove orphan test functions |

**`name` parameter:** The feature identifier, specified as a slash-separated path relative to `features_dir` (without `.feature` extension). For example, `shopping` resolves to `docs/features/shopping.feature`, and `be/shopping` resolves to `docs/features/be/shopping.feature`. Output mirrors the structure: `tests/features/shopping/default_test.py` or `tests/features/be/shopping/default_test.py`.

### generate

Reads `.feature` files from `features_dir`. Updates `.beehave/cache.json`. For each scenario without a matching test function:

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
    ...
```

Generated stubs use `...` (Ellipsis) as the function body. Body enforcement skips functions whose body is only `...` — once the user replaces `...` with real code, enforcement activates.

**Background stubs:** `generate` emits background functions before test functions in the same file. Background function names follow the pattern `background_<name>` where `<name>` is derived from the feature title (for feature-level background) or rule title (for rule-level background), using the same underscore conversion as test function names. All scenarios in the feature that share a background reference the same function via `@Background`.

**Appending to existing files:** When appending to an existing file, `generate` updates imports (adds any new symbols needed, e.g., `Example` when a Scenario Outline is added) and emits only new test function stubs. Background functions are emitted only when the file is first created; subsequent runs reuse the existing background function by name reference.

---

## File Conventions

```
docs/features/<feature_name>.feature     # Gherkin feature files
tests/features/<feature_name>/default_test.py  # Generated test stubs
```

---

## Architecture

### `beehave.decorators`

- `@Given(step_text)` — attaches step metadata (keyword: Given), vocabulary check
- `@When(step_text)` — attaches step metadata (keyword: When), vocabulary check
- `@Then(step_text)` — attaches step metadata (keyword: Then), vocabulary check
- `@And(step_text)` — continuation, inherits preceding step type
- `@But(step_text)` — continuation, inherits preceding step type
- `@Example(**kwargs)` — provides concrete values for Scenario Outline rows. Keys must match placeholder names exactly — unknown or missing keys → collection-time error. `@Example` is only valid on functions with `<placeholders>` in step text (which triggers `@given()` wrapping). `@Example` on a no-placeholder function → collection-time error.
- `@Background(func)` — references a function whose step decorators are verified against cached background steps. Number of `@Background` decorators must match the number of `Background:` sections in the feature/rule hierarchy.

### Strategy Resolution Trigger

When the decorator resolution phase detects that ANY step across all decorators contains `<placeholders>`, it resolves strategies and wraps the function with `@hypothesis.given(**strategies)`. This is independent of which step type (`@Given`, `@When`, `@Then`) contains the placeholders. The resolution fires once per function after all step decorators have been collected.

### `beehave.traceability`

- Parse `.feature` files (features, rules, backgrounds, scenarios, Examples tables)
- Extract scenarios, placeholders, Examples tables, background steps
- Derive function names from scenario titles
- Infer types from quoting and Examples columns
- Feature files are read as UTF-8 (transparently handles UTF-8 BOM)
- Lines starting with `#` (outside table cells) are comments and ignored. Inside table cells, `#` is literal text.

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
| `<placeholder>` in Background | Not supported (rejected by Cucumber) | Not supported — Background steps must be fixed literal text |
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
max_examples = 1                  # 0 = no random cases, N = N random Hypothesis cases
```

| Setting | Values | Default | Effect |
|---------|--------|---------|--------|
| `default_strategy` | `"integers"`, `"floats"`, `"text"`, `"booleans"` | `"integers"` | Strategy used when no other inference applies (priority 4) |
| `auto_inference` | `true`, `false` | `true` | If `false`, every `<variable>` must be manually defined at module level. Strategy inference from quoting convention and Examples table types is disabled. However, Examples table values are still read to generate `@Example` concrete values — they just don't infer strategies. At collection time, if a placeholder has no user-defined strategy and `auto_inference=false`, beehave raises an error listing all missing strategy definitions. |
| `features_dir` | any path | `"docs/features"` | Where beehave looks for `.feature` files |
| `tests_dir` | any path | `"tests/features"` | Where beehave generates test stubs |
| `max_examples` | any non-negative integer | `1` | Number of random Hypothesis cases for any scenario with `<placeholders>`. For Scenario Outline, `@Example` rows always run and this adds N random cases beyond them. For plain scenarios, N random cases total. 0 = no random exploration |

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
