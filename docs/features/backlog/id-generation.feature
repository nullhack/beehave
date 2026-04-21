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
