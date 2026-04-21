Feature: Config reading — read [tool.beehave] from pyproject.toml

  Beehave reads its configuration from the `[tool.beehave]` section of
  `pyproject.toml`. Supported keys include `features_path`, `framework`,
  `deletion_mode`, and `template_path`. Missing keys fall back to sensible
  defaults. Invalid configuration produces a descriptive hard error.

  Status: DRAFT
