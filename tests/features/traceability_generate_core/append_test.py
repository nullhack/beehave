def test_traceability_generate_core_7f6a3e8c(tmp_path, monkeypatch) -> None:
    """Generate appends a new function to an existing test file with interactive prompt.

    Given a test file that already exists with one test function
    When beehave generate tries to add another function to the same file
    Then the developer is prompted "file already exists. Add function? [y/N]"
    And if yes, the function is appended to the end of the file
    """
    from beehave.cli import _append_function

    existing_content = "def test_existing_abc12345():\n    ...\n"
    test_file = tmp_path / "existing_test.py"
    test_file.write_text(existing_content)

    new_function = "\n\ndef test_new_function_def45678():\n    ...\n"

    prompts = []

    def mock_input(prompt):
        prompts.append(prompt)
        return "y"

    monkeypatch.setattr("beehave.cli._is_interactive", lambda: True)
    monkeypatch.setattr("builtins.input", mock_input)

    _append_function(str(test_file), new_function)

    assert len(prompts) == 1
    assert "already exists" in prompts[0].lower()
    assert "Add function?" in prompts[0]

    result = test_file.read_text()
    assert "test_existing_abc12345" in result
    assert "test_new_function_def45678" in result
