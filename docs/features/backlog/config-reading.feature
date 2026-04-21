Feature: Config reading — read [tool.beehave] from pyproject.toml

  Beehave reads its configuration from the `[tool.beehave]` section of
  `pyproject.toml`. Supported keys include:
  - `features_path` — root path for `.feature` files (default: `docs/features/`)
  - `framework` — adapter to use (default: `pytest`)
  - `deletion_mode` — `warn` (default) or `error` when a `.feature` file is deleted
  - `template_path` — path to a custom template folder (optional)

  Missing keys fall back to sensible defaults. Invalid configuration produces a
  descriptive hard error. CLI flags (e.g. `--framework`, `--template-dir`) override
  the corresponding config keys.

  Status: BASELINED (2026-04-21)
