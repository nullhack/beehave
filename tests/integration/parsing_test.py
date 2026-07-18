from __future__ import annotations

import pytest

BACKGROUND_WITH_PLACEHOLDER_FEATURE = """\
Feature: Parsing
Background:
  Given a background step with <placeholder> token

Scenario: scenario
Given anything
"""

BACKGROUND_CLEAN_FEATURE = """\
Feature: Parsing
Background:
  Given a background step without placeholders

Scenario: scenario
Given anything
"""


def parse_feature_raises(feature_text: str) -> bool:
    from beehave.gherkin import parse_feature

    try:
        parse_feature(feature_text)
    except Exception:
        return True
    return False


@pytest.mark.pending
def test_background_step_with_placeholder_is_parse_error() -> None:
    assert parse_feature_raises(BACKGROUND_WITH_PLACEHOLDER_FEATURE)


@pytest.mark.pending
def test_background_step_without_placeholder_parses_cleanly() -> None:
    assert not parse_feature_raises(BACKGROUND_CLEAN_FEATURE)
