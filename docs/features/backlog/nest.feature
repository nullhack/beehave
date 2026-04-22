Feature: nest — bootstrap canonical directory structure

  Bootstraps the required directory structure and configuration for a new beehave project.
  Running `beehave nest` creates docs/features/{backlog,in-progress,completed}/, tests/features/,
  and .gitkeep files in each empty directory. It also injects a [tool.beehave] snippet into
  pyproject.toml if not already present. The command is additive and idempotent.

  Status: ELICITING

  Rules (Business):
  - Nest never removes or overwrites existing content
  - A project is considered already nested if docs/features/ contains any .feature file
  - nest --check verifies structure without modifying anything and exits non-zero if incomplete
  - nest --overwrite recreates managed directories from scratch

  Constraints:
  - Accepts --features-dir to override the default docs/features/ path
  - Safe to run in an existing Python project with unrelated files present
