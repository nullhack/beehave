Feature: ID generation — assign @id tags to untagged Examples

  Beehave detects Examples that lack an `@id` tag, generates a unique 8-character
  lowercase hexadecimal identifier, and writes it back into the `.feature` file.
  This makes every Example unambiguously addressable so that `sync` can map
  test stubs to their source criteria.

  Status: DRAFT
