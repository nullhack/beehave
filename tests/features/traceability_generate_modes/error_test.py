import json

from beehave.traceability import parse_feature as real_parse_feature


def test_traceability_generate_modes_a5c7e9f1(tmp_path, monkeypatch) -> None:
    """Generate handles features with no scenarios gracefully.

    Given a .feature file that has no scenarios
    When the developer runs beehave generate
    Then no test file is created
    And the output reports "no scenarios found" for that feature
    """
    from beehave.cli import generate

    features_dir = tmp_path / "docs" / "features"
    features_dir.mkdir(parents=True)
    (features_dir / "empty.feature").write_text(
        "Feature: Empty\n  Rule: Nothing here\n"
    )

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("beehave.cli._is_interactive", lambda: False)

    output = generate("empty", json_output=False)
    assert output is not None
    assert "no scenarios found" in output

    test_dir = tmp_path / "tests" / "features" / "empty"
    assert not test_dir.exists()


def test_traceability_generate_modes_f7e9d1b3(tmp_path, monkeypatch) -> None:
    """Generate skips malformed .feature files and reports errors.

    Given a malformed .feature file with an invalid syntax at line 12
    When the developer runs beehave generate
    Then a parse error is reported with the file path and line number
    And the malformed file is skipped
    And other .feature files continue to be processed
    """
    from beehave.cli import generate

    features_dir = tmp_path / "docs" / "features"
    features_dir.mkdir(parents=True)

    (features_dir / "good.feature").write_text(
        "Feature: Good\n  @id:ccc33333\n  Example: Good one\n    Given z\n"
    )
    (features_dir / "bad.feature").write_text("Feature: Bad\n")

    # Make parse_feature raise for the bad file to simulate a parse error
    original_open = open

    def patched_open(path, *args, **kwargs):
        result = original_open(path, *args, **kwargs)
        return result

    # Simulate a parse error by monkeypatching parse_feature
    call_count = {"n": 0}
    orig_parse = real_parse_feature

    def patched_parse(text):
        call_count["n"] += 1
        if "Feature: Bad" in text:
            raise SyntaxError(
                "unexpected token at line 1, expected 'Scenario' or 'Rule'"
            )
        return orig_parse(text)

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("beehave.cli._is_interactive", lambda: False)
    monkeypatch.setattr("beehave.cli.parse_feature", patched_parse)

    # JSON output to get structured results
    output = generate(json_output=True)
    data = json.loads(output)

    # Bad file should have an error entry
    bad_results = [r for r in data if "bad.feature" in r.get("file", "")]
    assert len(bad_results) == 1
    assert bad_results[0]["action"] == "error"
    assert "unexpected token" in bad_results[0]["error"]

    # Good file should still be processed (not blocked by bad file)
    good_results = [
        r
        for r in data
        if "good.feature" in r.get("file", "") or "good" in r.get("file", "")
    ]
    assert len(good_results) >= 1
    # The good file should produce a created/skipped_existing result
    good_actions = {r["action"] for r in good_results}
    assert good_actions & {"created", "skipped_existing", "appended"}
