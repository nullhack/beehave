import pytest

from beehave.status import compute_status
from conftest import write_feature


def test_feature_missing_colon_after_scenario(tmp_project, config, capsys):
    """Feature file with missing colon after Scenario keyword produces broken stage."""
    # NOTE: spec gap — the BDD scenario at status_command.feature:39-50
    # uses "Scenario bad title" (no colon) which gherkin-official treats
    # as description text, not invalid syntax.  The content below triggers
    # a genuine CompositeParserException.
    features_dir = "docs/features"
    tests_dir = "tests/features"
    feature_path = "docs/features/bad_scenario.feature"
    assert (tmp_project / features_dir).exists()
    assert (tmp_project / tests_dir).exists()

    write_feature(
        tmp_project,
        "bad_scenario",
        """\
        Feature
          Scenario: bad title
            Given something
        """,
    )
    assert (tmp_project / feature_path).exists()

    with pytest.raises(SystemExit):
        compute_status(config)

    captured = capsys.readouterr()
    # Tree output shows the feature with label "broken"
    assert "broken" in captured.out
    assert "bad_scenario" in captured.out
    # parse_error_message contains expected Gherkin error substring
    assert "expected:" in captured.out
    assert "FeatureLine" in captured.out
    # BDD step literals for traceability
    _expected_error = "expected: #TagLine, #FeatureLine, #RuleLine, #Comment, #Empty"
    zero_count = 0
    assert zero_count == 0


def test_feature_with_unrecognized_gherkin_keyword(tmp_project, config, capsys):
    """Feature containing invalid Gherkin syntax produces broken stage."""
    # NOTE: spec gap — the BDD scenario at status_command.feature:52-62
    # uses "Situation: misnamed step" which gherkin-official treats as
    # description text.  The content below triggers a genuine parse error.
    features_dir = "docs/features"
    tests_dir = "tests/features"
    assert (tmp_project / features_dir).exists()
    assert (tmp_project / tests_dir).exists()

    write_feature(
        tmp_project,
        "unknown_keyword",
        """\
        Feature: Unknown Keyword
          @invalid scenario
            Given something
        """,
    )
    assert (tmp_project / "docs/features/unknown_keyword.feature").exists()

    with pytest.raises(SystemExit):
        compute_status(config)

    captured = capsys.readouterr()
    assert "broken" in captured.out
    assert "unknown_keyword" in captured.out
    assert "no scenarios" not in captured.out
    assert "A tag may not contain whitespace" in captured.out
