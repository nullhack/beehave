# beehave v3 Specification

> A CLI that generates plain Hypothesis test stubs from Gherkin and checks body consistency. Tests import nothing from beehave at runtime.

---

## Product Definition

**IS:**
- A code generator (`beehave generate`) producing pure Hypothesis `@given()`/`@example()` stubs — processes one feature per invocation; users script loops for bulk processing
- A consistency checker (`beehave check`) that re-parses features, AST-parses tests, joins by function name, and reports violations in machine-parseable format
- A cleanup tool (`beehave clean`) that removes orphan test functions — if all functions are removed, the file retains its import block (the file is never deleted)
- Function-name-based traceability: `test_deposit_increases_balance` ↔ `Scenario: deposit increases balance`
- Background transparency: background steps merge into every scenario in scope — no background functions, no special syntax, just more commented steps in the generated stub

**IS NOT:** A test runner, runtime framework, step-definition engine, assertion DSL, synonym resolver, Hypothesis replacement, bulk processor, or `--dry-run` preview tool. No beehave imports appear in test code. `--dry-run` is acknowledged as a future enhancement but is not in v3 scope.

**Users:** Python developers writing property-based tests who want Gherkin as the spec source of truth.

### Error Handling

beehave reports errors immediately and exits non-zero. No partial output on failure.

| Condition | Behavior |
|-----------|----------|
| Feature file not found | Print error with searched path. Exit 1. |
| Gherkin parse error | Print error with `<file>:<line>` and parse message. Exit 1. |
| Python syntax error in test file | Print error with `<file>:<line>`. Skip the malformed file; other files continue. |
| Missing `features_dir` or `tests_dir` | Print error naming the missing directory and config key. Exit 1. |
| Invalid `default_strategy` value | Print error listing valid options (`text`, `integers`, `floats`, `booleans`). Exit 1. |
| Duplicate scenario title (name collision) | Print error naming both features and the colliding title. Exit 1. |

### Check Output Format

`beehave check` writes plain text to stdout. One line per violation, machine-parseable:

```
<path>:<line>: <error_type>: <message>
```

- `<path>`: relative file path (feature or test file)
- `<line>`: line number in the file (`0` if not applicable)
- `<error_type>`: `missing-placeholder` · `missing-literal` · `example-mismatch` · `orphan-test` · `orphan-scenario`
- `<message>`: human-readable description

Example output:

```
tests/features/bank_account/default_test.py:42: missing-placeholder: 'amount' not found in function body
tests/features/bank_account/default_test.py:55: orphan-test: 'test_withdrawal' has no matching scenario
docs/features/bank_account.feature:18: orphan-scenario: scenario 'overdraft rejected' has no test function
```

**Exit codes:** 0 if clean (no output). 1 if any violations found.

---

## Core Concepts

### 1:1 Traceability via Function Names

Every `Scenario` and `Scenario Outline` maps to exactly one test function. The function name is the lookup key, derived from the scenario title by the following deterministic algorithm:

1. **Trim** leading and trailing whitespace.
2. **Collapse** consecutive internal spaces to a single space.
3. **Replace** each space with an underscore (`_`).
4. **Prepend** `test_`.
5. **Validate** that the result is a valid Python identifier (`str.isidentifier()` returns `True`). If not, raise a parse error.

```
Scenario: deposit increases balance       →  test_deposit_increases_balance
Scenario:  extra   spaces   here          →  test_extra_spaces_here
```

No `@scenario` decorator. No `@id` tags. No cache file. At collection time, beehave re-parses all `.feature` files and AST-parses all test files, then joins on function name.

**Title rules:**

- **Characters:** Unicode letters, digits, and spaces only. Applies to Scenario, Scenario Outline, Feature, and Rule titles equally. Special characters would break generated file paths or Python identifiers.
- **Non-empty:** The title must be non-empty after trimming.
- **Scenario titles:** Globally unique across all features. Two scenario titles that collapse to the same function name produce a parse error.
- **Rule titles:** Unique within their parent Feature. Rule titles are used internally as keys for background lookup and in error messages — duplicate rule titles within a Feature produce a parse error. Per the Gherkin specification, rule names must be unique within their parent feature.
- **Feature titles:** Globally unique across all features. Feature titles determine the generated folder structure — `Feature: Bank` generates `tests/features/bank/`. Duplicate or special-character feature titles would create path collisions or invalid directories.

### Body Enforcement as the Consistency Mechanism

With no beehave imports at runtime, body enforcement replaces vocabulary enforcement. Instead of matching decorator text to `.feature` step text, beehave inspects the test function's AST to verify that every placeholder name and every literal value from the feature's steps is present. This guarantees the test exercises what the Gherkin describes — without any runtime coupling. The enforcement is purely structural: beehave checks for the *existence* of AST nodes, not their correctness.

### No Runtime Coupling

Tests import only `hypothesis`. `@given()`, `@example()`, and `@settings` are standard Hypothesis. beehave is a development-time tool — it never appears in `import` statements. There is no beehave runtime, no test runner integration, and no pytest plugins.

---

## Placeholder Syntax and Strategy Inference

`<name>` tokens in step text become Hypothesis parameters. Constraints on `name`:

| Constraint | Rule |
|-----------|------|
| Valid Python identifier | `str.isidentifier()` |
| Not a keyword | `not keyword.iskeyword()` |
| Not a builtin | `not hasattr(builtins, name)` |

No quoting convention — `'<name>'` and `<name>` in step text are treated identically. Both resolve to the same placeholder.

### Strategy Resolution

Priority (first match wins):

| Priority | Source | Strategy |
|----------|--------|----------|
| 1 (highest) | Module-level variable | User-defined expression |
| 2 | Examples table column type | Inferred from column values |
| 3 (lowest) | Default | Configured via `default_strategy` (default: `st.text()`) |

If no module-level override and no Examples table applies, the placeholder uses the configured default strategy (`st.text()` unless the user has changed `default_strategy` in `pyproject.toml`).

### Module-Level Variable Discovery (Priority 1)

To discover a user-defined strategy for placeholder `name`, beehave AST-parses the test file and checks for a top-level assignment of the form `name = <expr>`. The rules:

1. **Case-sensitive match.** The assigned variable name must exactly match the placeholder name.
2. **Top-level only.** Only module-level assignments count. Assignments inside functions, classes, or other compound statements are ignored.
3. **Assignments only, not imports.** `from hypothesis import strategies as name` does not count. Neither does `import name`. Only `name = <expr>` (an `Assign` node with a single `Name` target at module level).
4. **Expression not resolved.** beehave does not evaluate `<expr>` or validate that it produces a Hypothesis strategy. It only verifies the assignment exists. A typo on the right-hand side is the user's problem to debug at test runtime.

Example:

```python
from hypothesis import given, strategies as st

name = st.text()  # beehave finds this assignment; <name> uses st.text()

@given(name=name)
def test_bee_has_a_name(name):
    ...
```

### Examples Table Type Inference (Priority 2)

When a placeholder appears in a Scenario Outline's Examples table (and has no module-level override), the strategy is inferred from the column's values:

| Values in column | Inferred strategy |
|-------------------|-------------------|
| `100`, `200` | `st.integers()` |
| `30.5`, `50.0` | `st.floats()` |
| `"Alice"`, `"Bob"` | `st.text()` |
| `true`, `false` (case-insensitive) | `st.booleans()` |
| `[1, 2]` | `st.lists(st.integers())` |
| `{"a": 1}` | `st.dictionaries(st.text(), st.integers())` |
| Mixed types across rows | `st.integers()` + warning |

This type inference table is also used during `@example()` bijection checking — Examples table cell values are parsed into Python types using these rules before comparison.

---

## Body Enforcement

For each matched function–scenario pair, beehave inspects the function body's AST. Python comments are not represented in the AST and are ignored. Docstrings (`Expr(Constant(value=...))` nodes at the start of the function body) are excluded from enforcement checks. Only actual code nodes are examined.

### Stub Exemption

If the function body consists of a **single** `Expr(Constant(value=Ellipsis))` (i.e., `...`) or a **single** `Pass` node (i.e., `pass`), all body enforcement checks are skipped. This allows generated stubs to pass `beehave check` until the user implements them. A body containing anything beyond these two forms — even a docstring — is not a stub and is subject to all checks.

### Check 1: Placeholder Presence

Every `<name>` from the feature's steps must appear as a `Name` node in the function's AST. A `Name` node counts whether it appears in the **parameter list** or the **body** — a parameter binding in the function signature IS a `Name` reference and satisfies this check on its own, even if the name is never referenced in the body.

| Condition | Result |
|-----------|--------|
| `<name>` found as `Name` in parameters or body | Pass |
| `<name>` absent from both parameters and body | Fail — report the missing name(s) |

### Check 2: Literal Presence

Literal values extracted from step text must appear as `Constant` nodes in the function's AST.

**What counts as a literal:**

| Source | Extraction rule | Example step text | Extracted literal |
|--------|----------------|-------------------|-------------------|
| Numeric literal | A whitespace-delimited token consisting entirely of digits (matching `^\d+$`) | `the balance is 100` | `int(100)` |
| Quoted string | Text enclosed in double quotes (`"..."`) within Gherkin step text | `the value is "honey"` | `str("honey")` |
| Bare word | NOT extracted | `the value is honey` | *(nothing)* |

**Negative numbers are not supported as literals.** The token `-5` does not match `^\d+$` (it contains a hyphen) and is not extracted as a number. Users who need negative number enforcement should use `<param>` placeholders with a module-level strategy override. Only pure digit sequences qualify.

**Symbols attached to numbers** prevent extraction. The token `1%` does not match `^\d+$` and is not extracted. To enforce such values, enclose them in double quotes: `the rate is "1%"`.

**Quoted strings** are defined as any substring of Gherkin step text enclosed in double-quote characters (`"`). When beehave parses `Then the flavour is "honey"`, it extracts `honey` (without the quotes) as a string literal and checks that the function AST contains a `Constant(value="honey")`. Quoted strings are the only mechanism for enforcing non-numeric literal values. Bare words — even if they look meaningful — are NOT extracted and NOT enforced.

### Check 3: `@example()` Bijection

Each `@example()` decorator on the function must match exactly one row in the Scenario Outline's Examples table, and vice versa. Matching is by deep equality of Python values.

**Type coercion before comparison:** Examples table cell values are parsed into Python types using the type inference table above *before* comparison. So `100` in an Examples cell becomes Python `int(100)`, `30.5` becomes `float(30.5)`, `true` becomes `bool(True)`, and `"Alice"` becomes `str("Alice")`. The `@example()` decorator's keyword arguments are already Python literal values at AST-parse time. Deep equality is then checked between the coerced Examples row dict and the `@example()` keyword dict.

| Condition | Result |
|-----------|--------|
| Every row matches exactly one `@example()` and vice versa | Pass |
| Unmatched Examples row | Fail — report the unmatched row |
| Unmatched `@example()` decorator | Fail — report the unmatched decorator |

This check only applies to Scenario Outlines with Examples tables. Plain scenarios have no `@example()` bijection to verify.

### `@given()` Parameters: Not Validated

`@given()` kwargs are **not validated** by beehave — the user may add extra parameters (fixtures, helper values) beyond what the feature defines, or remove computed parameters. Feature placeholders that appear in `@given()` must have corresponding module-level strategy definitions if the configured default strategy (`st.text()` by default) is not desired. This is a user concern, not a beehave enforcement concern.

---

## Background

Background steps are transparently merged into every scenario in their scope. beehave prepends background step texts to the scenario's step texts before extracting placeholders and literals. Background steps are never mapped to their own test function — they only contribute to the scenarios in their scope.

| # | Rule |
|---|------|
| 1 | **No placeholders in Background.** Background steps must contain **no `<placeholders>`** — literal text only. If a `<placeholder>` token is found in a Background step, beehave raises a parse error naming the offending placeholder. |
| 2 | **Literal contribution.** Background literals are added to every scenario's literal enforcement set (Check 2 in Body Enforcement). A number or quoted string in a Background step must appear in every scenario's test function within scope. |
| 3 | **Scoping.** Feature-level background → all scenarios in the feature. Rule-level background → only scenarios within that rule. |
| 4 | **Ordering.** Step texts are concatenated in this order: feature background steps → rule background steps → scenario steps. Placeholders and literals are extracted from the concatenated sequence. |
| 5 | **Uniqueness.** At most one `Background:` block per Feature and at most one per Rule. Multiple `Background:` blocks at the same scope level produce a parse error. |

---

## Working Examples

### Example 1 — Plain scenario with params and background

```gherkin
Feature: Bank
  Background:
    Given a user exists

  Scenario: deposit increases balance
    Given a balance of <amount>
    When <deposit> is deposited
    Then the balance is <amount> plus <deposit>
```

```python
from hypothesis import given, strategies as st

amount = st.integers()
deposit = st.integers()

@given(amount=amount, deposit=deposit)
def test_deposit_increases_balance(amount, deposit):
    user = User()
    acct = Account(user, balance=amount)
    acct.deposit(deposit)
    assert acct.balance == amount + deposit
```

Background is transparent — the generated stub includes a commented `# Given a user exists` line, but there is no background function. The user handles setup in the body. `check` verifies `amount` and `deposit` appear as `Name` nodes.

### Example 2 — No-param scenario

```gherkin
  Scenario: new hive has no honey
    Given a new hive
    Then the honey level is 0
```

```python
def test_new_hive_has_no_honey():
    hive = Hive()
    assert hive.honey == 0
```

No `@given()` → plain function. Any test runner discovers it. Body must contain the literal `0` (enforced as a `Constant` node by `check`). No module-level variables needed — no placeholders to strategise.

### Example 3 — Default strategy (no override needed)

```gherkin
  Scenario: bee has a name
    Given a bee named <name>
    Then the bee responds to <name>
```

```python
from hypothesis import given, strategies as st

@given(name=st.text())
def test_bee_has_a_name(name):
    bee = Bee(name=name)
    assert bee.responds_to(name)
```

All placeholders default to `st.text()` (via `default_strategy`). No module-level variable, no quoting convention — `<name>` and `'<name>'` are treated identically. This is exactly what `beehave generate` produces: `@given(name=st.text())` with no user intervention required.

### Example 4 — User strategy override

```gherkin
  Scenario: balance never negative
    Given a balance of <amount>
    When <withdrawal> is withdrawn
    Then the balance is non negative
```

```python
from hypothesis import given, strategies as st

amount = st.integers(min_value=0)
withdrawal = st.integers(min_value=0)

@given(amount=amount, withdrawal=withdrawal)
def test_balance_never_negative(amount, withdrawal):
    assert amount - withdrawal >= 0
```

Module-level variables are the **only** mechanism to control strategy in v3. The user defines `amount` and `withdrawal` at module level. No per-placeholder config, no quoting convention.

### Example 5 — Scenario Outline with Examples

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
from hypothesis import given, example, strategies as st

@example(balance_a=100, balance_b=50, transfer=30, result_a=70, result_b=80)
@example(balance_a=200, balance_b=0, transfer=50, result_a=150, result_b=50)
@given(balance_a=st.integers(), balance_b=st.integers(), transfer=st.integers(),
       result_a=st.integers(), result_b=st.integers())
def test_specific_transfers(balance_a, balance_b, transfer, result_a, result_b):
    assert balance_a - transfer == result_a
    assert balance_b + transfer == result_b
```

`@example()` values are **Python typed**: `100` is an `int`, not the string `"100"`. Deep-equality bijection — each Examples row maps to exactly one `@example()` decorator. `@example()` outermost, `@given()` innermost (Hypothesis requirement). Strategy inferred from Examples table values (all integers → `st.integers()` at Priority 2); no module-level override needed.

### Example 6 — User removes computed params

```gherkin
  Scenario: spending reduces balance
    Given a balance of <initial>
    When <amount> is spent
    Then the balance is <remaining>
```

```python
from hypothesis import given, strategies as st

initial = st.integers()
amount = st.integers()

@given(initial=initial, amount=amount)
def test_spending_reduces_balance(initial, amount):
    remaining = initial - amount
    assert remaining >= 0
```

`<remaining>` is a computed value — the user omits it from `@given()`. `@given()` kwargs are **not validated** by `check`; the user controls what enters `@given()`. Body enforcement still requires `remaining` to appear as a `Name` node in the function body (it does: `remaining = ...`). The module-level variables override the default `st.text()` to `st.integers()` for both `initial` and `amount`.

---

## Architecture

| Module | Purpose |
|--------|---------|
| `beehave.gherkin` | Parse `.feature` files. Extract scenarios, placeholders, literals, examples. Enforce title rules (globally unique, Unicode letters/digits/spaces only). Merge background steps into scenarios. Return `dict[str, ScenarioInfo]` keyed by function name. |
| `beehave.discover` | AST-parse test files. Extract function names, `@given()` kwargs, `@example()` rows, body AST nodes (`Name`, `Constant`). Discover module-level strategy overrides by walking top-level `Assign` nodes where the target is a single `Name`. Return `dict[str, TestInfo]` keyed by function name. |
| `beehave.check` | Dict-join `ScenarioInfo` ↔ `TestInfo` on function name. Verify body enforcement (placeholder presence, literal presence), examples bijection, orphan detection. |
| `beehave.generate` | Produce stub `.py` files from `ScenarioInfo`. Emit `@given()` with inferred strategies, `@example()` rows, commented step text. **Skip existing functions** — only append truly new functions. Background steps appear as commented step text prepended to the scenario's steps. Create target directories as needed. |
| `beehave.clean` | Remove orphan test functions. If all functions are removed and only import statements remain, leave the file with those imports — do not delete the file. |
| `beehave.cli` | Entry point. `generate`, `check`, `clean` subcommands. No `fix` command, no `--dry-run` flag in v3. |

---

## CLI Commands

### `beehave generate <feature>`

**Input:** exactly one feature path relative to `features_dir` (no extension). `bank_account` → `docs/features/bank_account.feature`.

No bulk mode — `generate` accepts one feature path per invocation. To generate multiple features, script the command:

```bash
for f in bank_account transfer_ledger; do beehave generate "$f"; done
```

**Output:** test file at `tests/features/<path>/default_test.py`. Creates the full directory path if it does not exist.

**Behavior:**

1. Parse the feature file. On parse error: report path and line number, exit 1.
2. For each scenario, derive the function name from the scenario title.
3. **Skip existing functions** — if a test function with the same name already exists in the target file, do not overwrite. Only append truly new functions. Generate is idempotent.
4. For new functions, emit a stub containing: commented step text (background steps first, then scenario steps), `@given()` with inferred strategies, `@example()` from Examples table, `...` body.

**Exit codes:** 0 on success. 1 on any error.

### `beehave check [<feature>]`

**Input:** optional feature path. Omit → check all features in `features_dir`.

**Behavior:** parse features → AST-parse tests → dict join by function name → verify all invariants. Does not auto-fix — the user resolves drift manually.

**Output:** see [Check Output Format](#check-output-format). Exit 0 if clean, exit 1 if any violations.

### `beehave clean <feature>`

**Input:** exactly one feature path.

**Behavior:** remove test functions that have no matching scenario from the feature's test file. If all functions are removed, the file retains its import block — it is never deleted.

---

## File Conventions

```
docs/features/<path>/<name>.feature          # Gherkin feature files
tests/features/<path>/<name>/default_test.py # Test files
pyproject.toml                                # [tool.beehave] config
```

Feature path mirrors between `features_dir` and `tests_dir`. `bank_account` → `docs/features/bank_account.feature` + `tests/features/bank_account/default_test.py`.

One `.feature` file per feature, one test directory per feature (1:1 mapping). A feature may contain `Rule:` blocks — all scenarios within a feature (whether at top level or inside rules) map to test functions in the same test file. Rules do not create separate directories or files.

Example with rules:

```gherkin
Feature: Bank
  Background:
    Given a bank exists

  Scenario: new account starts at zero
    ...

  Rule: domestic transfers
    Background:
      Given domestic banking is enabled

    Scenario: local transfer
      ...
    Scenario: local transfer fee
      ...

  Rule: international transfers
    Background:
      Given SWIFT is available

    Scenario: wire transfer
      ...
```

All five scenarios (top-level + domestic rule + international rule) generate test functions in `tests/features/bank/default_test.py`. Backgrounds compose transparently — each scenario's commented steps include the applicable background chain.

**Title restrictions apply to all levels:** Feature, Rule, and Scenario titles must all contain only Unicode letters, digits, and spaces. Feature and Rule titles are used in folder structure, error messages, and internal keying — special characters would break generated paths or identifiers.

If a feature grows too large, split it into separate features.

---

## Configuration

```toml
[tool.beehave]
features_dir = "docs/features"
tests_dir = "tests/features"
default_strategy = "text"          # text → st.text() | integers → st.integers() | floats → st.floats() | booleans → st.booleans()
max_examples = 1                   # 0 = @example() rows only, N = N random Hypothesis cases beyond @example()
```

| Setting | Default | Description |
|---------|---------|-------------|
| `features_dir` | `"docs/features"` | Where `.feature` files live |
| `tests_dir` | `"tests/features"` | Where generated test files live |
| `default_strategy` | `"text"` | Fallback strategy for placeholders without a user override or Examples-table inference: `text` → `st.text()`, `integers` → `st.integers()`, `floats` → `st.floats()`, `booleans` → `st.booleans()` |
| `max_examples` | `1` | Controls `hypothesis.settings(max_examples)` for any test with `@given()`. For Scenario Outline, `@example()` rows always run and this adds N random cases beyond them. For plain scenarios with placeholders, N random cases total. `0` disables random exploration — only `@example()` rows run (Scenario Outline) or no random cases at all (plain scenario). |

No other configuration settings. No `--dry-run` flag in v3 (future scope).

---

## Gherkin Extensions and Constraints

| Feature | Standard Gherkin | beehave v3 |
|---------|-----------------|------------|
| `<param>` in steps | Only in Scenario Outline | Any step in any scenario |
| `<param>` in Background | Not supported | Not supported — background steps are literal-only |
| Background handling | Steps run before each scenario | Transparently merged into every scenario in scope; no emitted functions |
| Title uniqueness | Unique within Feature | Globally unique across all features |
| Title characters | Any text | Unicode letters, digits, spaces only |
| Tags | User-defined metadata | `@id` tags not used — function name is the sole lookup key |
| Scenario Outline Examples | Rows provide test data | Rows become `@example()` decorators via deep-equality bijection |
| Strategy control | N/A | Module-level variables only — no quoting convention, no per-placeholder config. Default: `st.text()` |

---

## What beehave IS NOT

- **Not a test runner.** beehave generates and checks test files. It does not execute tests.
- **Not a runtime framework.** Tests import only `hypothesis`. No `import beehave` ever appears in test code.
- **Not a step-definition engine.** No step registries, no decorator-to-step-text matching at runtime. Body enforcement is a static AST check.
- **Not an assertion DSL.** Use plain Python `assert`.
- **Not a synonym resolver.** Step text is not matched, normalized, or compared across steps.
- **Not a Hypothesis replacement.** beehave generates standard Hypothesis decorators.
- **Not a cache or state manager.** No `.beehave_cache` file, no database, no persistent state. Re-parsed from disk every invocation.
- **Not a code formatter or linter.** Use `ruff`, `black`, or similar tools.
