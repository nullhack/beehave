"""Tests for user overrides via custom template folder story."""

import pytest


@pytest.mark.skip(reason="not yet implemented")
def test_template_customization_21350e47() -> None:
    """
    Given: a project with custom templates in `my_templates/`
    When: the user runs "beehave sync --template-dir my_templates/"
    Then: stubs are generated using the custom templates
    """
    raise NotImplementedError


@pytest.mark.skip(reason="not yet implemented")
def test_template_customization_f971adb3() -> None:
    """
    Given: a project with `template_path = 'my_templates/'` in `[tool.beehave]`
    When: the user runs "beehave sync"
    Then: stubs are generated using the custom templates
    """
    raise NotImplementedError


@pytest.mark.skip(reason="not yet implemented")
def test_template_customization_7afb1c6f() -> None:
    """
    Given: a custom template folder with only a skip marker template
    When: beehave sync runs using the custom folder
    Then: the custom skip marker template replaces the built-in entirely
    """
    raise NotImplementedError

