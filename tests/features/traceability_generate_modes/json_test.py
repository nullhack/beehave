import json

from beehave.cli import generate


def test_traceability_generate_modes_2f8a6d4b(tmp_path, monkeypatch) -> None:
    """Generate produces machine-readable JSON output.

    Given a .feature file with orphan scenarios
    When the developer runs beehave generate --json
    Then the output is a JSON array of result objects
    And each object contains the file path, @id, scenario title, and action (created/appended/skipped)
    And --json implies non-interactive mode: existing files are appended without prompting
    """
    features_dir = tmp_path / "docs" / "features"
    features_dir.mkdir(parents=True)
    (features_dir / "billing.feature").write_text(
        "Feature: Billing\n"
        "  @id:aaa11111\n"
        "  Example: Calculate total\n"
        "    Given a cart with items\n"
    )

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("beehave.cli._is_interactive", lambda: True)

    output = generate("billing", json_output=True)
    assert output is not None

    data = json.loads(output)
    assert isinstance(data, list)
    assert len(data) >= 1

    result = data[0]
    assert "file" in result
    assert "id" in result
    assert result["id"] == "aaa11111"
    assert "scenario" in result
    assert result["scenario"] == "Calculate total"
    assert "action" in result
    assert result["action"] in ("created", "appended", "skipped_existing")

    # Verify test file was created (--json implies non-interactive, auto-creates)
    test_file = tmp_path / "tests" / "features" / "billing" / "default_test.py"
    assert test_file.exists()


def test_traceability_generate_modes_b3d5e7f9(tmp_path, monkeypatch) -> None:
    """--json auto-appends to existing files without prompt.

    Given a test file that already exists with one test function
    When the developer runs beehave generate --json
    Then the new function is appended without prompting
    And the JSON output includes an entry with action "appended"
    """
    features_dir = tmp_path / "docs" / "features"
    features_dir.mkdir(parents=True)
    (features_dir / "orders.feature").write_text(
        "Feature: Orders\n"
        "  @id:ddd44444\n"
        "  Example: Place order\n"
        "    Given a customer\n"
        "  @id:eee55555\n"
        "  Example: Cancel order\n"
        "    Given an order\n"
    )

    # Pre-create test dir with one existing function for the first scenario
    test_dir = tmp_path / "tests" / "features" / "orders"
    test_dir.mkdir(parents=True)
    existing_test = test_dir / "default_test.py"
    existing_test.write_text(
        "from beehave.decorators import Given, When, Then, Example\n"
        "from hypothesis import strategies as st\n\n\n"
        "def test_place_order_ddd44444():\n"
        "    ...\n"
    )

    monkeypatch.chdir(tmp_path)
    # Interactive mode would prompt, but --json auto-appends
    monkeypatch.setattr("beehave.cli._is_interactive", lambda: True)
    prompts = []

    def mock_input(prompt):
        prompts.append(prompt)
        return "n"  # Should NOT be called in --json mode

    monkeypatch.setattr("builtins.input", mock_input)

    output = generate("orders", json_output=True)
    data = json.loads(output)

    # No prompts should have been issued (--json implies non-interactive)
    assert len(prompts) == 0

    # One result should be "skipped_existing" (already had test)
    # One result should be "appended" (new function added to existing file)
    actions = [r["action"] for r in data]
    assert "skipped_existing" in actions
    assert "appended" in actions

    # The appended entry should reference the new scenario
    appended = [r for r in data if r["action"] == "appended"]
    assert appended[0]["id"] == "eee55555"

    # Verify file now contains both functions
    content = existing_test.read_text()
    assert "test_place_order_ddd44444" in content
    assert "eee55555" in content
