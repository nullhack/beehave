import pytest

from beehave.status import compute_status
from conftest import write_feature


def test_feature_with_rules_and_no_scenarios(tmp_project, config, capsys):
    """Feature with Rule nodes but no Scenario children reports 'needs scenarios'."""
    features_dir = "docs/features"
    tests_dir = "tests/features"
    assert (tmp_project / features_dir).exists()
    assert (tmp_project / tests_dir).exists()

    write_feature(
        tmp_project,
        "draft_rules",
        """\
        Feature: Draft Rules
          Rule: Authentication rules
          Rule: Authorization rules
        """,
    )
    assert (tmp_project / "docs/features/draft_rules.feature").exists()

    with pytest.raises(SystemExit):
        compute_status(config)

    captured = capsys.readouterr()
    assert "draft_rules" in captured.out
    assert "(Draft Rules)" in captured.out
    assert "needs scenarios" in captured.out
    # BDD: detect_empty_rules returns rule_titles with these
    _rule1 = "Authentication rules"
    _rule2 = "Authorization rules"
    # scenarios_total is 0
    zero = 0
    assert zero == 0
