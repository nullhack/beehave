Feature: sync-cleanup — handle orphaned and misplaced stubs

  Detects and reports on test stubs whose @id no longer matches any Example in any .feature file
  (orphans), and corrects stubs that are in the wrong directory by moving them to the right
  location. When a .feature file is deleted, beehave warns and the resulting orphan stubs are
  flagged by orphan detection. beehave never deletes stubs automatically.

  Status: ELICITING

  Rules (Business):
  - Orphaned stubs are warned about and never deleted automatically
  - A stub in the wrong directory is moved to the correct location, body preserved
  - A deleted .feature file triggers a warning

  Constraints:
  - Orphan: a test function whose name contains an @id absent from all .feature files
  - Path correction applies when @id matches but directory path does not
