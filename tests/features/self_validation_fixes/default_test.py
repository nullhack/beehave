import types

import pytest

from beehave.cli import generate
from beehave.decorators import _resolve_placeholder


def test_self_validation_fixes_f1a2b3c4(tmp_path, monkeypatch) -> None:
    """Text output shows created file path.

    Given a feature file "hive_tracking.feature" with 2 scenarios
    When beehave generates stubs in text mode
    Then the output contains "Created tests/features/hive_tracking/default_test.py"
    And the output contains the @id for each scenario
    """
    features_dir = tmp_path / "docs" / "features"
    features_dir.mkdir(parents=True)
    (features_dir / "hive_tracking.feature").write_text(
        "Feature: Hive Tracking\n"
        "  Rule: R1\n"
        "    @id:aaaa1111\n"
        "    Example: First scenario\n"
        "      Given a beehive\n"
        "    @id:bbbb2222\n"
        "    Example: Second scenario\n"
        "      Given a beehive\n"
    )

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("beehave.cli._is_interactive", lambda: False)

    output = generate("hive_tracking", json_output=False)

    assert output is not None
    assert "Created tests/features/hive_tracking/default_test.py" in output
    assert "aaaa1111" in output
    assert "bbbb2222" in output
    # All scenarios in a fresh file should be batched into one "Created" message,
    # not "Created" for the first + "Appended" for each subsequent scenario
    assert "Appended" not in output


def test_self_validation_fixes_d5e6f7a8(tmp_path, monkeypatch) -> None:
    """Appending shows file path with scenario @id.

    Given a feature file "hive_tracking.feature" with 3 scenarios and an existing stub for the first
    When beehave generates stubs in text mode
    Then the output contains "Appended to tests/features/hive_tracking/default_test.py"
    And the output contains the @id for the new scenarios
    """
    features_dir = tmp_path / "docs" / "features"
    features_dir.mkdir(parents=True)
    (features_dir / "hive_tracking.feature").write_text(
        "Feature: Hive Tracking\n"
        "  Rule: R1\n"
        "    @id:aaaa1111\n"
        "    Example: First scenario\n"
        "      Given a beehive\n"
        "    @id:bbbb2222\n"
        "    Example: Second scenario\n"
        "      Given a beehive\n"
        "    @id:cccc3333\n"
        "    Example: Third scenario\n"
        "      Given a beehive\n"
    )

    # Pre-create test dir with stub for the first scenario
    test_dir = tmp_path / "tests" / "features" / "hive_tracking"
    test_dir.mkdir(parents=True)
    existing_test = test_dir / "default_test.py"
    existing_test.write_text("def test_first_scenario_aaaa1111():\n    ...\n")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("beehave.cli._is_interactive", lambda: False)

    output = generate("hive_tracking", json_output=False)

    assert output is not None
    assert "Appended to tests/features/hive_tracking/default_test.py" in output
    assert "bbbb2222" in output
    assert "cccc3333" in output
    # All new scenarios should be in a single "Appended to" message
    appended_lines = [line for line in output.split("\n") if "Appended to" in line]
    assert len(appended_lines) == 1


def test_self_validation_fixes_b9c0d1e2(tmp_path, monkeypatch) -> None:
    """Multiple scenarios produce one import block.

    Given a feature file "hive_tracking.feature" with 3 scenarios
    When beehave generates stubs
    Then the output file contains "from beehave.decorators import" exactly once
    And each scenario has its own test function
    """
    features_dir = tmp_path / "docs" / "features"
    features_dir.mkdir(parents=True)
    (features_dir / "hive_tracking.feature").write_text(
        "Feature: Hive Tracking\n"
        "  Rule: R1\n"
        "    @id:aaaa1111\n"
        "    Example: First scenario\n"
        "      Given a beehive\n"
        "    @id:bbbb2222\n"
        "    Example: Second scenario\n"
        "      Given a beehive\n"
        "    @id:cccc3333\n"
        "    Example: Third scenario\n"
        "      Given a beehive\n"
    )

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("beehave.cli._is_interactive", lambda: False)

    generate("hive_tracking", json_output=False)

    test_file = tmp_path / "tests" / "features" / "hive_tracking" / "default_test.py"
    assert test_file.exists()
    file_content = test_file.read_text()

    # Only one import block, even with multiple scenarios
    assert file_content.count("from beehave.decorators import") == 1

    # Each scenario has its own test function
    assert "aaaa1111" in file_content
    assert "bbbb2222" in file_content
    assert "cccc3333" in file_content


def test_self_validation_fixes_f3a4b5c6(tmp_path, monkeypatch) -> None:
    """Generated test directory has __init__.py.

    Given a feature file "hive_tracking.feature" with 1 scenario
    When beehave generates stubs
    Then tests/features/hive_tracking/__init__.py exists
    And tests/features/hive_tracking/default_test.py exists
    """
    features_dir = tmp_path / "docs" / "features"
    features_dir.mkdir(parents=True)
    (features_dir / "hive_tracking.feature").write_text(
        "Feature: Hive Tracking\n"
        "  Rule: R1\n"
        "    @id:aaaa1111\n"
        "    Example: Only scenario\n"
        "      Given a beehive\n"
    )

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("beehave.cli._is_interactive", lambda: False)

    generate("hive_tracking", json_output=False)

    test_dir = tmp_path / "tests" / "features" / "hive_tracking"
    assert (test_dir / "__init__.py").exists()
    assert (test_dir / "default_test.py").exists()


def test_self_validation_fixes_d7e8f9a0(tmp_path, monkeypatch) -> None:
    """Generated stubs are skipped by pytest.

    Given a feature file "hive_tracking.feature" with 1 scenario
    When beehave generates stubs
    Then pytest collects the stub as SKIPPED
    And the stub body raises NotImplementedError
    """
    features_dir = tmp_path / "docs" / "features"
    features_dir.mkdir(parents=True)
    (features_dir / "hive_tracking.feature").write_text(
        "Feature: Hive Tracking\n"
        "  Rule: R1\n"
        "    @id:aaaa1111\n"
        "    Example: Only scenario\n"
        "      Given a beehive\n"
    )

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("beehave.cli._is_interactive", lambda: False)

    generate("hive_tracking", json_output=False)

    test_file = tmp_path / "tests" / "features" / "hive_tracking" / "default_test.py"
    file_content = test_file.read_text()

    assert '@pytest.mark.skip(reason="not yet implemented")' in file_content
    assert "raise NotImplementedError" in file_content


def test_self_validation_fixes_b1c2d3e4(tmp_path, monkeypatch) -> None:
    """Stub has decorators matching .feature Gherkin steps.

    Given a feature file "hive_tracking.feature" with a scenario having Given/When/Then steps
    When beehave generates stubs
    Then the stub function has @Given, @When, @Then decorators matching the feature steps
    And the stub function parameters include the <placeholder> names from the steps
    """
    features_dir = tmp_path / "docs" / "features"
    features_dir.mkdir(parents=True)
    (features_dir / "hive_tracking.feature").write_text(
        "Feature: Hive Tracking\n"
        "  Rule: R1\n"
        "    @id:abcd1234\n"
        "    Example: Steps with placeholders\n"
        "      Given a hive with <quantity> bees\n"
        "      When the beekeeper adds <count> bees\n"
        "      Then the hive has <quantity> + <count> bees\n"
    )

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("beehave.cli._is_interactive", lambda: False)

    generate("hive_tracking", json_output=False)

    test_file = tmp_path / "tests" / "features" / "hive_tracking" / "default_test.py"
    file_content = test_file.read_text()

    # The test function should have step decorators matching the Gherkin steps
    assert '@Given("a hive with <quantity> bees")' in file_content
    assert '@When("the beekeeper adds <count> bees")' in file_content
    assert '@Then("the hive has <quantity> + <count> bees")' in file_content

    # The function parameters should include placeholder names
    assert "quantity" in file_content
    assert "count" in file_content


def test_self_validation_fixes_a5b6c7d8() -> None:
    """Missing strategy variable produces a warning.

    Given a test using <quantity> placeholder with no quantity_strategy defined
    When beehave resolves strategies at import time
    Then a UserWarning is emitted mentioning "quantity" and "st.integers() fallback"
    """
    test_module = types.ModuleType("test_module")

    with pytest.warns(UserWarning, match=r"quantity.*st\.integers\(\) fallback"):
        _resolve_placeholder("quantity", test_module)
