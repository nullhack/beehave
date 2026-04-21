Feature: Hatch — generate example/demo feature files

  `beehave hatch` writes a set of bee-themed example `.feature` files into the
  features directory tree. The generated content showcases every beehave
  capability (auto-ID, deprecation, Scenario Outlines, Backgrounds, data tables,
  multilingual parsing) so that a developer can see the full feature set in
  action without writing Gherkin from scratch.

  The generated files are framework-agnostic — they are plain Gherkin `.feature`
  files with no dependency on any test framework. `hatch` is strictly a content
  generator; directory structure setup is `nest`'s responsibility.

  Status: BASELINED (2026-04-21)
