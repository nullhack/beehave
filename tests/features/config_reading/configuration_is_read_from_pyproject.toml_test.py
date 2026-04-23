"""Tests for configuration is read from pyproject.toml story."""

import pytest


@pytest.mark.skip(reason="not yet implemented")
def test_config_reading_efed7ea2() -> None:
    """
    Given: a `pyproject.toml` with `[tool.beehave]` section containing `framework = 'pytest'`
    When: beehave reads configuration
    Then: the framework is set to pytest
    """
    raise NotImplementedError


@pytest.mark.skip(reason="not yet implemented")
def test_config_reading_8c2aaae3() -> None:
    """
    Given: a `pyproject.toml` without `[tool.beehave]` section
    When: beehave reads configuration
    Then: all configuration values use defaults
    """
    raise NotImplementedError


@pytest.mark.skip(reason="not yet implemented")
def test_config_reading_7c4abdc7() -> None:
    """
    Given: a `pyproject.toml` with `[tool.beehave]` but no `framework` key
    When: beehave reads configuration
    Then: the framework defaults to pytest
    """
    raise NotImplementedError

