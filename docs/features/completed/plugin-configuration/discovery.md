# Discovery: plugin-configuration

## State
Status: BASELINED

## Entities
| Type | Name | Candidate Class/Method | In Scope |
|------|------|----------------------|----------|
| Noun | features folder path | path to `docs/features/` directory | Yes |
| Noun | `pyproject.toml` | project configuration file | Yes |
| Noun | `[tool.beehave]` section | configuration section in `pyproject.toml` | Yes |
| Noun | default path | `docs/features/` relative to project root | Yes |
| Verb | read config | parse `[tool.beehave]` from `pyproject.toml` | Yes |
| Verb | resolve path | make the configured path absolute relative to project root | Yes |
| Verb | fall back to default | use `docs/features/` if no config present | Yes |

## Rules
- Configuration lives in `[tool.beehave]` section of `pyproject.toml`
- The only configurable option is `features_path` (path to the features directory)
- Default value: `docs/features/` relative to the project root (where `pyproject.toml` lives)
- The path is resolved relative to the directory containing `pyproject.toml`
- If `pyproject.toml` does not exist or has no `[tool.beehave]` section, the default is used silently
- The plugin is always-on; there is no enable/disable switch

## Constraints
- Must not fail if `pyproject.toml` is absent — fall back to default
- Must not fail if `[tool.beehave]` section is absent — fall back to default
- Must produce a clear error if `features_path` is configured but the directory does not exist

## Questions
| ID | Question | Answer | Status |
|----|----------|--------|--------|
| Q1 | What is the exact config key name? | `features_path` under `[tool.beehave]` | ANSWERED |
| Q2 | Should an invalid/missing configured path be a hard error or a warning? | Hard error — if the user explicitly configured a path that doesn't exist, fail loudly | ANSWERED |
