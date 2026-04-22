Feature: id-generation — assign @id tags to untagged Examples

  Assigns stable, unique 8-character lowercase hex @id tags to any Example in a .feature file
  that does not already have a valid one. beehave writes the tag back in-place, preserving all
  whitespace and formatting exactly. A valid existing @id is never replaced. Malformed tags
  (empty value or non-hex characters) are treated as missing and replaced.

  Status: ELICITING

  Rules (Business):
  - @id values are unique project-wide across all .feature files
  - Developer-supplied valid @id tags are respected and never overwritten
  - Collision on generation triggers a silent retry until a unique id is produced
  - Assignment is top-to-bottom within each file

  Constraints:
  - In-place write preserves all existing whitespace and formatting
  - Dry-run / preview is provided by beehave status, not a separate mode
