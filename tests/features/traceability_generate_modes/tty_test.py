from beehave.cli import generate


def test_traceability_generate_modes_e1a3c5d7(tmp_path, monkeypatch) -> None:
    """Non-TTY mode auto-appends without prompting.

    Given a test file that already exists and stdout is not a TTY
    When the developer runs beehave generate
    Then the new function is appended without prompting
    And the output is human-readable text format
    """
    features_dir = tmp_path / "docs" / "features"
    features_dir.mkdir(parents=True)
    (features_dir / "shipping.feature").write_text(
        "Feature: Shipping\n"
        "  @id:fff66666\n"
        "  Example: Ship order\n"
        "    Given a packed order\n"
        "  @id:ggg77777\n"
        "  Example: Track shipment\n"
        "    Given a shipped order\n"
    )

    # Pre-create test dir with one existing function
    test_dir = tmp_path / "tests" / "features" / "shipping"
    test_dir.mkdir(parents=True)
    existing_test = test_dir / "default_test.py"
    existing_test.write_text(
        "from beehave.decorators import Given, When, Then, Example\n"
        "from hypothesis import strategies as st\n\n\n"
        "def test_ship_order_fff66666():\n"
        "    ...\n"
    )

    monkeypatch.chdir(tmp_path)
    # Non-TTY: _is_interactive returns False
    monkeypatch.setattr("beehave.cli._is_interactive", lambda: False)
    prompts = []

    def mock_input(prompt):
        prompts.append(prompt)
        return "n"

    monkeypatch.setattr("builtins.input", mock_input)

    output = generate("shipping", json_output=False)
    assert output is not None

    # No prompts should have been issued (non-TTY auto-appends)
    assert len(prompts) == 0

    # Output is human-readable text, NOT JSON
    assert (
        output.startswith("Skipped")
        or output.startswith("Appended")
        or "Skipped" in output
    )
    # Should not be valid JSON array
    import json

    try:
        json.loads(output)
        is_json = True
    except json.JSONDecodeError, ValueError:
        is_json = False
    assert not is_json, "Output should be human-readable text, not JSON"

    # Verify file now contains the appended function
    content = existing_test.read_text()
    assert "test_ship_order_fff66666" in content
    assert "ggg77777" in content
