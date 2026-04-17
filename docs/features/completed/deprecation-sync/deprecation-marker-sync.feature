Feature: Deprecation marker sync
  As a developer
  I want @pytest.mark.deprecated to be toggled on test functions whenever the @deprecated tag changes in the .feature file
  So that deprecated acceptance criteria are automatically skipped across all feature stages

  @id:f9b636df
  Example: Deprecated Example in a backlog feature gets the deprecated marker
    Given a backlog feature with an Example tagged @deprecated whose test stub lacks @pytest.mark.deprecated
    When pytest is invoked
    Then the test stub has @pytest.mark.deprecated applied

  @id:fc372f15
  Example: Deprecated Example in a completed feature gets the deprecated marker
    Given a completed feature with an Example tagged @deprecated whose test stub lacks @pytest.mark.deprecated
    When pytest is invoked
    Then the test stub has @pytest.mark.deprecated applied

  @id:7fcee92a
  Example: Deprecated marker is removed when @deprecated tag is removed
    Given a feature with an Example that no longer has the @deprecated tag but whose test stub has @pytest.mark.deprecated
    When pytest is invoked
    Then @pytest.mark.deprecated is removed from that test stub
