Feature: Quote Escaping in Stubs

  Generated test stub files must always contain syntactically valid Python. When .feature step text contains quote characters, the generator must escape them so that the resulting decorator string is a valid Python string literal. Without this, generated files cause SyntaxError on import and are completely unusable.

  Rules (Business):
  - When _generate_stub_content() writes a step decorator, it must ensure the step text is properly escaped so the resulting Python string literal is syntactically valid
  - When step text contains the chosen outer quote character, the generator must either switch to the alternate quote character or escape the inner quotes
  - A generated test stub must always be importable by Python — passing py_compile.compile() is a structural invariant of the StubGenerated event
  - The developer can run pytest on generated files without encountering SyntaxError when step text contains quotes
  - GenerateStub can produce valid Python decorators when step text contains any combination of quote characters

  Constraints:
  - Generated code validity (QA8): when step text contains quotes, the generated decorator is valid Python; all generated files pass py_compile.compile()
  - Idempotency: generating the same stub multiple times produces identical, syntactically valid output
  - Safety: generate is additive-only — it never modifies existing function bodies
  - Recommended escaping strategy: always use single quotes for the outer decorator string; escape any single quotes within the step text with backslash
  - MoSCoW: Must

  ## Changes

  | Session | Change |
  |---------|--------|
  | 2026-05-11 | Created: PP8 — unescaped quotes in generated decorator strings produce SyntaxError |
