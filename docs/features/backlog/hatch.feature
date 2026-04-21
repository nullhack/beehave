Feature: Hatch — generate example/demo feature files

  `beehave hatch` generates bee-themed example `.feature` files that demonstrate
  beehave conventions and Gherkin best practices. It is strictly a demo / onboarding
  tool: it creates content, not structure, and operates independently of `nest`.

  The generated files are placed in the configured features path. They are full
  valid Gherkin with `@id` tags so that running `beehave sync` immediately produces
  corresponding test stubs — giving the developer an end-to-end example of the
  tool's workflow.

  `hatch` is idempotent: running it again overwrites the demo files with fresh
  copies.

  Status: BASELINED (2026-04-21)

  Rules (Business):
  - Generated content is fictional (bee-world theme) and never touches real
    business logic.
  - Output is valid Gherkin that passes beehave's own parser.

  Constraints:
  - `hatch` requires the features path to exist; it does not create directories.

  Rule: Generate demo feature files
    As a new beehave user
    I want example `.feature` files to exist in my project
    So that I can see what good Gherkin looks like and validate the sync
      workflow end-to-end

    @id:a5b6c7d8
    Example: Creates example feature in backlog folder
      Given a project with a `docs/features/backlog/` directory
      When I run `beehave hatch`
      Then one or more `.feature` files appear in `docs/features/backlog/`
        containing bee-themed scenarios

    @id:b6c7d8e9
    Example: Generated features contain valid Gherkin
      Given `beehave hatch` has been run
      When beehave parses the generated `.feature` files
      Then no parse errors occur

    @id:c7d8e9f0
    Example: Generated files have @id tags on every Example
      Given `beehave hatch` has been run
      When I inspect the generated `.feature` files
      Then every Example has an `@id:<8-char-hex>` tag

    @id:d8e9f0a1
    Example: Overwrites existing demo files on re-run
      Given a project where `beehave hatch` was already run
      When I run `beehave hatch` again
      Then the demo files are overwritten with fresh content and the modified
        timestamp is updated
