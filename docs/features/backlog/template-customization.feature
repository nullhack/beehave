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
