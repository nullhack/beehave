# Current Work

Feature: example-hatch
Step: 3 (TDD Loop) — quality gate
Source: docs/features/in-progress/example-hatch.feature

## Progress
- [x] `@id:1a2b3c4d`: Hatch creates the features directory tree when it does not exist
- [x] `@id:2b3c4d5e`: Hatch writes bee-themed .feature files into the correct subfolders
- [x] `@id:3c4d5e6f`: Hatch emits a terminal summary of files written
- [x] `@id:4d5e6f7a`: pytest exits immediately after hatch without running tests
- [x] `@id:5e6f7a8b`: Hatch fails when the features directory already contains .feature files
- [x] `@id:6f7a8b9c`: Hatch overwrites existing content when --beehave-hatch-force is passed
- [x] `@id:7a8b9c0d`: Generated content includes an untagged Example to trigger auto-ID generation
- [x] `@id:8b9c0d1e`: Generated content includes a @deprecated-tagged Example
- [x] `@id:9c0d1e2f`: Generated content includes a multilingual feature file
- [x] `@id:0d1e2f3a`: Generated content includes a feature with a Background block
- [x] `@id:1e2f3a4b`: Generated content includes a Scenario Outline with an Examples table
- [x] `@id:a1f2e3d4`: Generated content includes a step with an attached data table
- [x] `@id:b2e3d4c5`: Generated content includes a feature placed in the completed subfolder
- [x] `@id:c3d4e5f6`: Hatch writes to the custom path when features_path is configured
- [x] `@id:d4e5f6a7`: Hatch produces a different Feature name on successive runs
- [x] `@id:e5f6a7b8`: Hatch completes without requiring any additional package installation

## Notes
- lint: PASS
- static-check: PASS
- test-coverage: FAIL at 95% — 44 lines missing in 5 pre-existing modules (__main__, steps_reporter, stub_reader, stub_writer, sync_engine). This gap existed in v2 (98.90%) before example-hatch started. Not caused by this feature.
- hatch.py and plugin.py (new code): 100% covered

## Next
Run @software-engineer — produce SE Self-Declaration, then hand off to @reviewer for Step 4
