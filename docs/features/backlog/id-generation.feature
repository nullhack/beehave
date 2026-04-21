Feature: ID generation — assign @id tags to untagged Examples

  Beehave detects Examples that lack an `@id` tag, generates a unique 8-character
  lowercase hexadecimal identifier, and writes it back into the `.feature` file
  in-place, preserving all whitespace and formatting exactly.

  ID assignment is project-wide: uniqueness is enforced across all `.feature` files.
  If a developer has already added their own `@id:<value>` before running beehave,
  beehave respects it as-is and never overwrites or regenerates it. Malformed tags
  (e.g. `@id:` with no value, or `@id:ZZZZZZZZ` with non-hex characters) are treated
  as missing — a new valid ID is generated and replaces the malformed one.

  Collision during generation is resolved by silent retry until a unique value is found.
  Ordering follows top-to-bottom file order. The operation is idempotent: an Example
  with a valid `@id` is left completely untouched on subsequent runs.

  A Python API entry point is available: `from beehave import assign_ids`.
  Dry-run preview is provided by `beehave status` — there is no separate preview mode
  for id-generation.

  Status: BASELINED (2026-04-21)

  Rules (Business):
  - Every Example in every `.feature` file must have exactly one `@id` tag.
  - beehave-generated IDs are 8-char lowercase hex; user-provided IDs of any
    format are accepted as-is once valid.
  - Malformed `@id` tags are treated as missing and replaced.
  - Feature files are only ever mutated to add missing `@id` tags; no other edits.

  Constraints:
  - Validity check: an `@id:` value must contain exactly 8 hexadecimal characters.
  - Uniqueness scope is the entire project (all `.feature` files combined).

  Rule: Detect and tag untagged Examples
    As a PO writing acceptance criteria
    I want beehave to add stable IDs to Examples so that test stubs can map
      to criteria unambiguously
    So that I never have to manage IDs manually

    @id:e7f8a9b0
    Example: Tags single untagged Example
      Given a `.feature` file containing one Example with no `@id` tag
      When I run `beehave sync` or `beehave assign-ids`
      Then the Example now has an `@id:<8-char-hex>` tag inserted above it

    @id:f8a9b0c1
    Example: Tags multiple untagged Examples in file order
      Given a `.feature` file containing three untagged Examples in sequence
      When I run `beehave sync`
      Then each Example receives a unique `@id` tag in top-to-bottom order

    @id:a9b0c1d2
    Example: Preserves existing formatting and comments
      Given a `.feature` file with a blank line above an untagged Example
      When beehave writes the `@id` tag
      Then the blank line is preserved and the `@id` tag is inserted directly
        above the `Example:` keyword

    @id:b0c1d2e3
    Example: Ignores already tagged Examples
      Given a `.feature` file with one tagged and one untagged Example
      When beehave assigns IDs
      Then the tagged Example is untouched and the untagged one gets a new ID

  Rule: Validate existing IDs
    As a developer who may have hand-written IDs
    I want beehave to tell me when my IDs are malformed
    So that I can fix them before sync proceeds

    @id:c1d2e3f4
    Example: Replaces empty value @id:
      Given a `.feature` file containing `@id:` (no value)
      When beehave validates IDs
      Then the empty tag is replaced with a valid generated `@id` and a warning
        is emitted

    @id:d2e3f4a5
    Example: Replaces non-hex characters
      Given a `.feature` file containing `@id:XYZ12345`
      When beehave validates IDs
      Then the invalid tag is replaced with a valid generated `@id` and a warning
        is emitted

  Rule: Enforce uniqueness across the project
    As a team with many feature files
    I want all IDs to be unique project-wide
    So that test stubs never map to the wrong Example

    @id:e3f4a5b6
    Example: Re-rolls on collision
      Given a `.feature` file where an existing `@id:a1b2c3d4` is already used
        in another `.feature` file, and beehave is about to generate the same ID
      When beehave assigns IDs
      Then it retries with a new random value until the ID is unique project-wide

    @id:f4a5b6c7
    Example: Warns on user-supplied duplicate
      Given two `.feature` files both containing `@id:deadbeef`
      When beehave validates IDs
      Then a warning is emitted naming both files and the duplicate tag is left
        as-is (user owns the ID)
