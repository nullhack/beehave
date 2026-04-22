Feature: pytest-adapter — built-in adapter for the pytest framework

  Implements the adapter contract for pytest. Supplies the pytest-specific stub conventions used
  by sync-create, sync-update, and parameter-handling when pytest is the active framework.

  Status: ELICITING

  Rules (Business):
  - All generated pytest stubs are immediately runnable with pytest without modification

  Constraints:
  - Skip marker: @pytest.mark.skip(reason="not yet implemented")
  - Deprecated marker: @pytest.mark.deprecated
  - Parametrize: @pytest.mark.parametrize(...)
  - Function prefix: test_; return type: -> None; body: ...
