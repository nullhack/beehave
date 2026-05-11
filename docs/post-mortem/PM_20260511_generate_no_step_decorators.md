# PM_20260511_generate_no_step_decorators: Generated stubs omit step decorators

## Failed At

CLI `generate()` — dogfood user: generated stub `def test_adding_nectar_to_the_honey_store_a1b2c3d4()` has no `@Given`, `@When`, `@Then` decorators matching the feature's Gherkin steps. The stub is a bare function that doesn't use beehave's core decorator mechanism.

## Root Cause

`_generate_stub_content()` receives `steps=[]` and `examples=[]` from `_process_scenario()`. The caller passes empty lists because `_process_scenario()` doesn't extract steps from the parsed scenario. The `parse_feature()` function returns `Scenario` objects with only `name` and `id_tag` — no step data. The step extraction logic exists in `_parse_feature_steps()` but is not connected to the generate flow.

The stub generation has step-decorator-producing code (lines 199-215 of cli.py), but it's dead code because `steps` is always `[]`.

## Missed Gate

The `traceability_generate_core` feature tested that stubs contain the correct function name and ID, but did not test that stubs include step decorators matching the feature file. The `fix` command was designed to add missing decorators later, but the generate command should produce a usable starting point.

## Fix

Connect `_parse_feature_steps()` to `_process_scenario()` so that steps are extracted from the feature file and passed to `_generate_stub_content()`. The function already handles step decoration — it just needs non-empty input.

## Restart Check

Generate stubs for `decorator_test`. The generated file should contain `@Given("a hive with <initial> grams of honey")`, `@When(...)`, `@Then(...)` decorators on each test function, with matching function parameters.
