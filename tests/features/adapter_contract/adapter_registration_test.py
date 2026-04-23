"""Tests for adapter registration story."""

import pytest


@pytest.mark.skip(reason="not yet implemented")
def test_adapter_contract_1635448b() -> None:
    """
    Given: `framework = 'pytest'` is set in `[tool.beehave]`
    When: beehave sync runs
    Then: the pytest adapter is used
    """
    raise NotImplementedError


@pytest.mark.skip(reason="not yet implemented")
def test_adapter_contract_db46e7bb() -> None:
    """
    Given: `framework = 'pytest'` is set in `[tool.beehave]`
    When: the user runs "beehave sync --framework unittest"
    Then: the unittest adapter is used
    """
    raise NotImplementedError


@pytest.mark.skip(reason="not yet implemented")
def test_adapter_contract_b2c4e9ca() -> None:
    """
    Given: no framework is specified in config or CLI
    When: beehave sync runs
    Then: the pytest adapter is used
    """
    raise NotImplementedError

