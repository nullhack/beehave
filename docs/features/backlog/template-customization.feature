Feature: template-customization — user-defined stub templates

  Allows developers to override the built-in adapter stub templates with their own. A custom
  template folder is a full replacement for the built-in templates when specified. This enables
  teams with non-standard conventions to generate stubs that match their style without forking
  beehave.

  Status: BASELINED (2026-04-22)

  Rules (Business):
  - Built-in adapter templates are used when no custom folder is specified
  - A custom template folder fully replaces the built-in for matched template files

  Constraints:
  - Custom folder specified via --template-dir flag or template_path config key in [tool.beehave]

  Rule: Default template usage
    As a developer
    I want beehave to use built-in templates when I have not configured a custom folder
    So that beehave works out of the box without any template configuration

    @id:bf0a3c49
    Example: Built-in templates are used when template_path is not set
      Given no template_path in [tool.beehave] and no --template-dir flag
      When beehave sync generates a stub
      Then the stub matches the built-in adapter template format

  Rule: Custom template override
    As a developer
    I want to point beehave at my own template folder
    So that generated stubs match my team's coding conventions

    @id:cf259a6c
    Example: Custom template replaces built-in when template_path is set
      Given template_path = "templates/beehave" in [tool.beehave] and a custom stub template in that folder
      When beehave sync generates a stub
      Then the stub matches the custom template, not the built-in

    @id:99c97725
    Example: --template-dir flag overrides template_path config for the current invocation
      Given template_path = "templates/beehave" in [tool.beehave]
      When beehave sync is invoked with --template-dir other/templates
      Then stubs are generated using the other/templates folder

    @id:bb612744
    Example: Non-existent custom template folder raises an error
      Given template_path points to a directory that does not exist
      When beehave sync runs
      Then beehave exits with an error identifying the missing template directory

  Rule: Partial custom template
    As a developer
    I want to override only specific template files and fall back to built-ins for the rest
    So that I only need to maintain the templates I actually customise

    @id:ad3b70dc
    Example: Missing template file in custom folder falls back to built-in
      Given a custom template folder that contains only a stub template but not a file header template
      When beehave sync generates a new test file
      Then the file header comes from the built-in template and the stub body from the custom template
