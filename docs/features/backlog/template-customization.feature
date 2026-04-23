Feature: Template Customization — user-defined stub templates
Status: BASELINED (2026-04-23)

Users can override built-in adapter templates by pointing to a custom template
folder via `--template-dir` flag or `[tool.beehave]` config key `template_path`.
Custom templates fully replace the built-in for matched template files.

Rule: Default templates come from the adapter

  @id:e0314dc7
  Example: Built-in templates are used by default
    Given a project using the pytest adapter with no custom template path
    When beehave generates stubs
    Then the built-in pytest adapter templates are used

Rule: User overrides via custom template folder

  @id:21350e47
  Example: Custom template folder via CLI flag
    Given a project with custom templates in `my_templates/`
    When the user runs "beehave sync --template-dir my_templates/"
    Then stubs are generated using the custom templates

  @id:f971adb3
  Example: Custom template folder via config
    Given a project with `template_path = 'my_templates/'` in `[tool.beehave]`
    When the user runs "beehave sync"
    Then stubs are generated using the custom templates

  @id:7afb1c6f
  Example: Custom folder is a full replacement
    Given a custom template folder with only a skip marker template
    When beehave sync runs using the custom folder
    Then the custom skip marker template replaces the built-in entirely
