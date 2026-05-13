from pathlib import Path

from beehave.cli import _ensure_test_directory, _generate_stub_content
from beehave.traceability import parse_feature


def test_traceability_generate_core_e4c1b9d3(tmp_path) -> None:
    """Generate creates a new test file with directory creation for a feature with no existing tests.

    Given a .feature file "balance_accounting.feature" with scenarios but no matching test directory
    When the developer runs beehave generate
    Then tests/features/balance_accounting/default_test.py is created
    And it contains imports, strategy variables, step decorators, @Example decorators, and a function with ... body
    And the directory tests/features/balance_accounting/ is created if it does not exist
    """
    feature_text = (
        "Feature: Balance Accounting\n"
        "  Rule: R1\n"
        "    @id:abc12345\n"
        "    Example: First scenario\n"
        "      Given something\n"
    )
    scenarios = parse_feature(feature_text)
    scenario = scenarios[0]

    # Directory does not exist yet
    test_dir = str(tmp_path / "tests" / "features" / "balance_accounting")
    assert not Path(test_dir).exists()

    # Ensure directory is created
    result_dir = _ensure_test_directory(test_dir)
    assert Path(result_dir).exists()
    assert Path(result_dir).is_dir()

    # Generate stub content and write file
    content = _generate_stub_content(
        scenario_name=scenario.name.value,
        scenario_id=scenario.id_tag.value,
        steps=["Given something"],
        examples=[],
    )
    test_file = Path(result_dir) / "default_test.py"
    test_file.write_text(content)

    # Verify file contents
    file_content = test_file.read_text()
    assert "import" in file_content
    assert "st.integers()" in file_content
    assert "Example" in file_content
    assert "@Given" in file_content
    assert "def test_first_scenario_abc12345" in file_content
    assert "..." in file_content
