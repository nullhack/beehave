Feature: Quote Escaping in Stubs

  Generated test stub files must always contain syntactically valid Python. When .feature step text contains quote characters, the generator must escape them so that the resulting decorator string is a valid Python string literal. Without this, generated files cause SyntaxError on import and are completely unusable.

  Constraints:
  - Generated code validity (QA8): when step text contains quotes, the generated decorator is valid Python; all generated files pass py_compile.compile()
  - Idempotency: generating the same stub multiple times produces identical, syntactically valid output
  - Safety: generate is additive-only — it never modifies existing function bodies
  - Escaping strategy: always use single quotes for the outer decorator string; escape any single quotes within the step text with backslash
  - MoSCoW: Must

  ## Changes

  | Session | Change |
  |---------|--------|
  | 2026-05-11 | Created: PP8 — unescaped quotes in generated decorator strings produce SyntaxError |
  | 2026-05-11 | Break-down: 1 Rule (quote escaping produces valid Python), 6 Must Examples covering double quotes, single quotes, both, baseline, multi-step, idempotency |

  Rule: Step decorators produce syntactically valid Python for all step text regardless of quote content
    As a Property-Based TDD Developer using `beehave generate`
    I want step decorators in generated stubs to properly escape quote characters found in step text
    So that I can import and run the generated file without encountering SyntaxError

    @id:a1b2c3d4
    Example: Double quotes in step text are preserved when using single-quoted outer string
      Given a .feature file with step text containing double quotes: `hive "Alpha" has 10 frames`
      When the developer runs `beehave generate` for that feature
      Then the generated step decorator uses a single-quoted outer string: `@Given('hive "Alpha" has 10 frames')`
      And the generated file passes `py_compile.compile()`

    @id:e5f6a7b8
    Example: Single quotes in step text are escaped with backslash
      Given a .feature file with step text containing a single quote: `it's a valid hive`
      When the developer runs `beehave generate` for that feature
      Then the generated step decorator escapes the inner single quote: `@Given('it\'s a valid hive')`
      And the generated file passes `py_compile.compile()`

    @id:9c0d1e2f
    Example: Both single and double quotes in step text are handled together
      Given a .feature file with step text containing both quote types: `the bee said "it's pollen"`
      When the developer runs `beehave generate` for that feature
      Then the generated step decorator preserves double quotes and escapes the single quote: `@Given('the bee said "it\'s pollen"')`
      And the generated file passes `py_compile.compile()`

    @id:3a4b5c6d
    Example: Step text without quotes produces single-quoted decorator unchanged
      Given a .feature file with step text containing no quotes: `a hive with 10 frames`
      When the developer runs `beehave generate` for that feature
      Then the generated step decorator uses a single-quoted outer string: `@Given('a hive with 10 frames')`
      And the generated file passes `py_compile.compile()`

    @id:7e8f9a0b
    Example: Multiple steps with quotes in one scenario all produce valid decorators
      Given a .feature scenario with a Given step `hive "Alpha" exists` and a Then step `it's healthy`
      When the developer runs `beehave generate` for that feature
      Then the Given decorator is `@Given('hive "Alpha" exists')`
      And the Then decorator is `@Then('it\'s healthy')`
      And the entire generated file passes `py_compile.compile()`

    @id:c1d2e3f4
    Example: Re-running generate with quoted step text produces identical valid output
      Given a generated stub file for a step containing quotes
      When the developer runs `beehave generate` again for the same feature
      Then the generated output is identical to the first run
      And both runs produce files that pass `py_compile.compile()`
