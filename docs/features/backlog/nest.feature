Feature: Nest — bootstrap canonical directory structure

  `beehave nest` initialises the canonical beehave directory structure in a
  project. On a green-field project it creates five directories — the root
  `docs/features/` folder, its three stage subfolders (`backlog/`,
  `in-progress/`, `completed/`), and `tests/features/` — each seeded with a
  `.gitkeep` so they are tracked by git. It also injects a `[tool.beehave]`
  configuration snippet into `pyproject.toml` if the section is absent.

  The command is additive and idempotent: running it a second time only creates
  whatever is still missing and emits a configurable warning (or error) when the
  project is already fully nested. A project is considered "already nested" when
  `docs/features/` already contains at least one `.feature` file.

  Additional flags:
  - `--features-dir <path>` — override the default `docs/features/` root.
  - `--check`               — verify structure without modifying anything;
                              exits non-zero if any managed path is absent.
  - `--overwrite`           — recreate the structure from scratch.

  `beehave nest` never generates `.feature` content — that is `hatch`'s job.
  It never refuses or prompts because of unrelated files already present.

  Status: DRAFT
