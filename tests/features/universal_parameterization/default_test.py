"""Test stubs for universal_parameterization feature.

Generated from: docs/features/universal_parameterization.feature
Rule: Plain Scenario steps with <placeholder> extract variables regardless of scenario type
Rule: Generated stubs include function parameters for placeholders without Examples table
Rule: Single-quoted placeholder forces string type
"""

import re

from beehave.cli import _generate_stub_content
from beehave.traceability import Placeholder, parse_feature


def test_universal_parameterization_6f8d808c() -> None:
    """A plain Scenario with <name> in step text extracts the placeholder.

    Given a .feature file with "Scenario: simple bee" and step "Given a bee named <bee_name> with <frames> frames"
    When the parser processes the file
    Then the scenario has placeholders ["bee_name", "frames"]
    """
    text = (
        "Feature: hive\n"
        "  Scenario: simple bee\n"
        "    Given a bee named <bee_name> with <frames> frames\n"
    )
    scenarios = parse_feature(text)

    assert scenarios[0].placeholders == (Placeholder("bee_name"), Placeholder("frames"))


def test_universal_parameterization_955893de() -> None:
    """A plain Scenario without <placeholder> has no placeholders extracted.

    Given a .feature file with "Scenario: static test" and step "Given a bee named zoom"
    When the parser processes the file
    Then the scenario has no placeholders
    """
    text = "Feature: hive\n  Scenario: static test\n    Given a bee named zoom\n"
    scenarios = parse_feature(text)

    assert scenarios[0].placeholders == ()


def test_universal_parameterization_794a895b() -> None:
    """Stub for plain Scenario with <placeholder> has function parameters.

    Given a .feature file with "Scenario: bee flight" and step "Given a bee flies <distance> meters"
    And no Examples table
    When beehave generate creates the test stub
    Then the test function has parameter "distance"
    And the @given decorator uses strategy resolution for "distance"
    """
    stub = _generate_stub_content(
        scenario_name="bee flight",
        scenario_id="abc12345",
        steps=[("Given", "a bee flies <distance> meters")],
        examples=[],
        include_imports=False,
    )

    # Verify function definition includes the placeholder as a parameter
    assert re.search(r"def test_bee_flight_abc12345\(distance\):", stub)


def test_universal_parameterization_c4c97662() -> None:
    """Stub for plain Scenario with multiple placeholders has all parameters.

    Given a .feature file with "Scenario: hive health" with steps containing <colony_size> and <nectar_units>
    And no Examples table
    When beehave generate creates the test stub
    Then the test function has parameters ["colony_size", "nectar_units"]
    """
    stub = _generate_stub_content(
        scenario_name="hive health",
        scenario_id="def67890",
        steps=[
            ("Given", "a colony of <colony_size> bees"),
            ("And", "<nectar_units> units of nectar"),
        ],
        examples=[],
        include_imports=False,
    )

    # Verify function definition includes both placeholders as parameters
    assert re.search(
        r"def test_hive_health_def67890\(colony_size, nectar_units\):", stub
    )


def test_universal_parameterization_a22d6bd3() -> None:
    """'<name>' in step text forces string strategy.

    Given a .feature file with step "Given a bee named '<bee_name>'"
    When the parser extracts placeholders
    Then "bee_name" is marked as string type
    And strategy resolution uses st.text() instead of module-level variable lookup
    """
    text = (
        "Feature: hive\n  Scenario: string type\n    Given a bee named '<bee_name>'\n"
    )
    scenarios = parse_feature(text)

    bee_name_placeholder = scenarios[0].placeholders[0]
    assert bee_name_placeholder.name == "bee_name"
    assert bee_name_placeholder.is_string is True


def test_universal_parameterization_1c2d3e4f() -> None:
    """Unquoted <name> uses normal strategy resolution.

    Given a .feature file with step "Given <frames> frames"
    When the parser extracts placeholders
    Then "frames" uses normal strategy resolution (module-level variable lookup, fallback st.integers())
    """
    text = "Feature: hive\n  Scenario: normal strategy\n    Given <frames> frames\n"
    scenarios = parse_feature(text)

    frames_placeholder = scenarios[0].placeholders[0]
    assert frames_placeholder.name == "frames"
    assert frames_placeholder.is_string is False
