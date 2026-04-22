Feature: template-customization — user-defined stub templates

  Allows developers to override the built-in adapter stub templates with their own. A custom
  template folder is a full replacement for the built-in templates when specified. This enables
  teams with non-standard conventions to generate stubs that match their style without forking
  beehave.

  Status: ELICITING

  Rules (Business):
  - Built-in adapter templates are used when no custom folder is specified
  - A custom template folder fully replaces the built-in for matched template files

  Constraints:
  - Custom folder specified via --template-dir flag or template_path config key in [tool.beehave]
