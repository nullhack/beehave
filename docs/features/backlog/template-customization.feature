Feature: Template customization — user-defined stub templates

  End users may override the built-in adapter templates by pointing beehave to a
  custom template folder. The override is specified via the `--template-dir` CLI
  flag or the `template_path` key in `[tool.beehave]` in `pyproject.toml`.

  A custom template folder is a full replacement for the matched built-in template
  files — it overrides the built-in adapter templates entirely for any file present
  in the custom folder. This allows teams to enforce their own coding standards,
  docstring formats, or marker styles without forking the adapter code.

  Built-in adapter templates remain the default when no custom folder is configured.

  Status: BASELINED (2026-04-21)

  Rules (Business):
  - Only files present in the custom folder override the built-in; missing files
    fall back to the built-in template.
  - Custom templates must expose the same variables the adapter contract expects
    (e.g. `function_name`, `docstring`, `id`, `markers`).

  Constraints:
  - Custom template syntax must match whatever the core renderer expects (e.g.
    Jinja2, string.Template). This is documented in the adapter contract.

  Rule: Override specific templates via custom folder
    As a team lead enforcing coding standards
    I want beehave to use my custom skip marker instead of the built-in one
    So that our test suite follows our conventions

    @id:e5f6a7b8
    Example: Custom skip marker template
      Given a custom template folder containing a `skip.txt` with the text
        `@pytest.mark.skip("TODO")` instead of the default reason string
      When beehave sync runs with `--template-dir` pointing to that folder
      Then every generated skip marker uses `TODO` as the reason

    @id:f6a7b8c9
    Example: Unchanged templates fall back to built-in
      Given a custom template folder containing only `skip.txt`
      When beehave sync runs with `--template-dir` pointing to that folder
      Then the skip marker is from the custom template but deprecated and
        parametrize markers use the built-in templates

  Rule: Validate custom template variables
    As a developer writing a custom template
    I want beehave to tell me if my template references an unknown variable
    So that I catch typos early

    @id:a7b8c9d0
    Example: Missing variable causes hard error
      Given a custom template with `{{ unknown_variable }}`
      When beehave attempts to render it
      Then the command exits with an error naming the unknown variable and
        the template file path
