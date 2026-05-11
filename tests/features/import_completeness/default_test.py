"""Test stubs for import_completeness feature.

Generated from: docs/features/import_completeness.feature
Rule: Import line includes all decorator types used in the scenario
Rule: Generated stubs are always syntactically valid Python
"""

import py_compile
import tempfile

from beehave.cli import _generate_stub_content


def _assert_compiles(source: str) -> None:
    """Assert that source code passes py_compile.compile()."""
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
        f.write(source.encode())
        f.flush()
        py_compile.compile(f.name, doraise=True)


def _import_line(source: str) -> str:
    """Extract the beehave.decorators import line from generated source."""
    for line in source.splitlines():
        if "beehave.decorators" in line:
            return line
    return ""


def test_import_completeness_f1e2d3c4() -> None:
    """Stub with And step imports And decorator.

    Given a .feature file with steps using Given and And keywords
    When beehave generate creates the test stub
    Then the import line includes "And" alongside "Given"
    And the file passes py_compile.compile()
    """
    steps = [("Given", "a setup"), ("And", "another setup")]
    stub = _generate_stub_content(
        scenario_name="And step test",
        scenario_id="f1e2d3c4",
        steps=steps,
        examples=[],
    )
    imp = _import_line(stub)
    assert "And" in imp, f"Import line missing 'And': {imp}"
    assert "Given" in imp, f"Import line missing 'Given': {imp}"
    _assert_compiles(stub)


def test_import_completeness_b5a69788() -> None:
    """Stub with But step imports But decorator.

    Given a .feature file with steps using Then and But keywords
    When beehave generate creates the test stub
    Then the import line includes "But" alongside "Then"
    And the file passes py_compile.compile()
    """
    steps = [("Then", "a result"), ("But", "not another result")]
    stub = _generate_stub_content(
        scenario_name="But step test",
        scenario_id="b5a69788",
        steps=steps,
        examples=[],
    )
    imp = _import_line(stub)
    assert "But" in imp, f"Import line missing 'But': {imp}"
    assert "Then" in imp, f"Import line missing 'Then': {imp}"
    _assert_compiles(stub)


def test_import_completeness_87655926() -> None:
    """Stub with Given/When/Then only does not import And/But.

    Given a .feature file with steps using only Given, When, Then keywords
    When beehave generate creates the test stub
    Then the import line includes "Given, When, Then"
    And the import line does not include "And" or "But"
    """
    steps = [("Given", "a setup"), ("When", "an action"), ("Then", "a result")]
    stub = _generate_stub_content(
        scenario_name="Basic keywords test",
        scenario_id="87655926",
        steps=steps,
        examples=[],
    )
    imp = _import_line(stub)
    assert "Given" in imp, f"Import line missing 'Given': {imp}"
    assert "When" in imp, f"Import line missing 'When': {imp}"
    assert "Then" in imp, f"Import line missing 'Then': {imp}"
    assert "And" not in imp, f"Import line should not include 'And': {imp}"
    assert "But" not in imp, f"Import line should not include 'But': {imp}"


def test_import_completeness_01fe4990() -> None:
    """Stub with all five decorator types is valid Python.

    Given a .feature file with steps using Given, When, Then, And, But keywords
    When beehave generate creates the test stub
    Then the import line includes "Given, When, Then, And, But"
    And the file passes py_compile.compile()
    """
    steps = [
        ("Given", "a setup"),
        ("When", "an action"),
        ("Then", "a result"),
        ("And", "another result"),
        ("But", "not a failure"),
    ]
    stub = _generate_stub_content(
        scenario_name="All five keywords test",
        scenario_id="01fe4990",
        steps=steps,
        examples=[],
    )
    imp = _import_line(stub)
    for name in ("Given", "When", "Then", "And", "But"):
        assert name in imp, f"Import line missing '{name}': {imp}"
    _assert_compiles(stub)


def test_import_completeness_3d5935ce() -> None:
    """Stub with only And steps is valid Python.

    Given a .feature file with a scenario containing only And and But steps (following a Given from Background)
    When beehave generate creates the test stub
    Then the import line includes "And, But"
    And the file passes py_compile.compile()
    """
    steps = [("And", "additional setup"), ("But", "not a teardown")]
    stub = _generate_stub_content(
        scenario_name="Only And But test",
        scenario_id="3d5935ce",
        steps=steps,
        examples=[],
    )
    imp = _import_line(stub)
    assert "And" in imp, f"Import line missing 'And': {imp}"
    assert "But" in imp, f"Import line missing 'But': {imp}"
    _assert_compiles(stub)
