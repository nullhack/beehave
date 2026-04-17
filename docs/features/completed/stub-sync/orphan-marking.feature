Feature: Orphan test marking
  As a developer
  I want test functions with no matching @id in any .feature file to be marked as skipped
  So that stale tests do not pollute the test suite without being silently ignored

  @id:9d7a0b34
  Example: Orphan test receives skip marker
    Given a test file containing a test function whose @id hex does not match any Example in any .feature file
    When pytest is invoked
    Then that test function has @pytest.mark.skip(reason="orphan: no matching @id in .feature files") applied

  @id:67192894
  Example: Previously orphaned test loses skip marker when a matching Example is added
    Given a test function marked as orphan and a .feature file that now contains a matching @id Example
    When pytest is invoked
    Then the orphan skip marker is removed from that test function
