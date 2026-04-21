Feature: Pytest adapter — generate pytest test stubs

  The pytest adapter produces pytest-compatible test stubs: top-level functions
  named `test_<feature_slug>_<@id>`, with `@pytest.mark.skip` for new stubs,
  `@pytest.mark.deprecated` where applicable, `@pytest.mark.parametrize` for
  Scenario Outlines, and verbatim step docstrings. It is the default and first
  framework adapter.

  Status: DRAFT
