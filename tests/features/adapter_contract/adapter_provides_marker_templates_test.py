"""Tests for adapter provides marker templates story."""

import pytest


@pytest.mark.skip(reason="not yet implemented")
def test_adapter_contract_39abfbe8() -> None:
    """
    Given: the pytest adapter is active
    Then: it provides:
      | Template          | Value                                             |
      | Skip marker       | `@pytest.mark.skip(reason="not yet implemented")` |
      | Deprecated marker | `@pytest.mark.deprecated`                         |
      | Parametrize       | `@pytest.mark.parametrize(...)`                   |
      | Stub header       | pytest imports and conventions                    |
    """
    raise NotImplementedError

