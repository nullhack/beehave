"""Test stubs for quote_escaping feature.

Generated from: docs/features/quote_escaping.feature
Rule: Step decorators produce syntactically valid Python for all step text regardless of quote content
"""

import py_compile

from beehave.cli import _generate_stub_content


def test_quote_escaping_a1b2c3d4(tmp_path) -> None:
    """Double quotes in step text are preserved when using single-quoted outer string.

    Given a .feature file with step text containing double quotes: `hive "Alpha" has 10 frames`
    When the developer runs `beehave generate` for that feature
    Then the generated step decorator uses a single-quoted outer string: `@Given('hive "Alpha" has 10 frames')`
    And the generated file passes `py_compile.compile()`
    """
    content = _generate_stub_content(
        scenario_name="Double quotes test",
        scenario_id="a1b2c3d4",
        steps=[("Given", 'hive "Alpha" has 10 frames')],
        examples=[],
        include_imports=True,
    )
    test_file = tmp_path / "default_test.py"
    test_file.write_text(content)

    # Verify decorator format: single-quoted outer string, double quotes preserved inside
    assert "@Given('hive \"Alpha\" has 10 frames')" in content

    # Verify file is valid Python
    py_compile.compile(str(test_file), doraise=True)


def test_quote_escaping_e5f6a7b8(tmp_path) -> None:
    """Single quotes in step text are escaped with backslash.

    Given a .feature file with step text containing a single quote: `it's a valid hive`
    When the developer runs `beehave generate` for that feature
    Then the generated step decorator escapes the inner single quote: `@Given('it\\'s a valid hive')`
    And the generated file passes `py_compile.compile()`
    """
    content = _generate_stub_content(
        scenario_name="Single quotes test",
        scenario_id="e5f6a7b8",
        steps=[("Given", "it's a valid hive")],
        examples=[],
        include_imports=True,
    )
    test_file = tmp_path / "default_test.py"
    test_file.write_text(content)

    # Verify decorator format: single quotes escaped with backslash
    assert "@Given('it\\'s a valid hive')" in content

    # Verify file is valid Python
    py_compile.compile(str(test_file), doraise=True)


def test_quote_escaping_9c0d1e2f(tmp_path) -> None:
    """Both single and double quotes in step text are handled together.

    Given a .feature file with step text containing both quote types: `the bee said "it's pollen"`
    When the developer runs `beehave generate` for that feature
    Then the generated step decorator preserves double quotes and escapes the single quote: `@Given('the bee said "it\\'s pollen"')`
    And the generated file passes `py_compile.compile()`
    """
    content = _generate_stub_content(
        scenario_name="Both quotes test",
        scenario_id="9c0d1e2f",
        steps=[("Given", 'the bee said "it\'s pollen"')],
        examples=[],
        include_imports=True,
    )
    test_file = tmp_path / "default_test.py"
    test_file.write_text(content)

    # Verify decorator format: double quotes preserved, single quote escaped
    assert "@Given('the bee said \"it\\'s pollen\"')" in content

    # Verify file is valid Python
    py_compile.compile(str(test_file), doraise=True)


def test_quote_escaping_3a4b5c6d(tmp_path) -> None:
    """Step text without quotes produces single-quoted decorator unchanged.

    Given a .feature file with step text containing no quotes: `a hive with 10 frames`
    When the developer runs `beehave generate` for that feature
    Then the generated step decorator uses a single-quoted outer string: `@Given('a hive with 10 frames')`
    And the generated file passes `py_compile.compile()`
    """
    content = _generate_stub_content(
        scenario_name="No quotes baseline",
        scenario_id="3a4b5c6d",
        steps=[("Given", "a hive with 10 frames")],
        examples=[],
        include_imports=True,
    )
    test_file = tmp_path / "default_test.py"
    test_file.write_text(content)

    # Verify decorator uses single-quoted outer string
    assert "@Given('a hive with 10 frames')" in content

    # Verify file is valid Python
    py_compile.compile(str(test_file), doraise=True)


def test_quote_escaping_7e8f9a0b(tmp_path) -> None:
    """Multiple steps with quotes in one scenario all produce valid decorators.

    Given a .feature scenario with a Given step `hive "Alpha" exists` and a Then step `it's healthy`
    When the developer runs `beehave generate` for that feature
    Then the Given decorator is `@Given('hive "Alpha" exists')`
    And the Then decorator is `@Then('it\\'s healthy')`
    And the entire generated file passes `py_compile.compile()`
    """
    content = _generate_stub_content(
        scenario_name="Multi step quotes",
        scenario_id="7e8f9a0b",
        steps=[("Given", 'hive "Alpha" exists'), ("Then", "it's healthy")],
        examples=[],
        include_imports=True,
    )
    test_file = tmp_path / "default_test.py"
    test_file.write_text(content)

    # Verify Given decorator format: double quotes preserved in single-quoted string
    assert "@Given('hive \"Alpha\" exists')" in content

    # Verify Then decorator format: single quote escaped with backslash
    assert "@Then('it\\'s healthy')" in content

    # Verify entire file is valid Python
    py_compile.compile(str(test_file), doraise=True)


def test_quote_escaping_c1d2e3f4(tmp_path) -> None:
    """Re-running generate with quoted step text produces identical valid output.

    Given a generated stub file for a step containing quotes
    When the developer runs `beehave generate` again for the same feature
    Then the generated output is identical to the first run
    And both runs produce files that pass `py_compile.compile()`
    """
    steps = [("Given", 'the hive "Alpha" has 10 frames')]

    content1 = _generate_stub_content(
        scenario_name="Idempotent test",
        scenario_id="c1d2e3f4",
        steps=steps,
        examples=[],
        include_imports=True,
    )
    content2 = _generate_stub_content(
        scenario_name="Idempotent test",
        scenario_id="c1d2e3f4",
        steps=steps,
        examples=[],
        include_imports=True,
    )

    # Verify identical output across runs
    assert content1 == content2

    # Write both and verify they are valid Python
    test_file1 = tmp_path / "run1_test.py"
    test_file1.write_text(content1)
    py_compile.compile(str(test_file1), doraise=True)

    test_file2 = tmp_path / "run2_test.py"
    test_file2.write_text(content2)
    py_compile.compile(str(test_file2), doraise=True)
