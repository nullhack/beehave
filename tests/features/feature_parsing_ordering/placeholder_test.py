import pytest

from beehave.validation import validate_placeholders


@pytest.mark.skip(reason="not yet implemented")
def test_placeholder_5b7f2d9e():
    """All placeholders match function parameters

    Given a step "a user with balance <initial>" and a function with parameter initial
    When beehave validates placeholders
    Then no mismatch is reported
    """
    raise NotImplementedError


@pytest.mark.skip(reason="not yet implemented")
def test_placeholder_d3a6c1b8():
    """Missing function parameter for placeholder

    Given a step "a user with balance <initial>" and a function with no initial parameter
    When beehave validates placeholders
    Then a mismatch is reported: "<initial> not found in function parameters"
    """
    raise NotImplementedError
