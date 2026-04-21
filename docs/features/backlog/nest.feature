Feature: Nest — bootstrap canonical directory structure

  `beehave nest` creates the canonical features directory structure under the
  configured (or default) features path. It ensures the three stage subfolders
  (`backlog/`, `in-progress/`, `completed/`) exist so that subsequent `sync`,
  `status`, and `hatch` commands can operate on a well-known layout.

  Status: DRAFT
