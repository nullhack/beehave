# Integration contract for `beehave.gherkin` parser-level invariants.
#
# Closes the traceability gap on interview L1: "no placeholders are allowed in
# Background steps" (data-model §2.7 - binding parse-time invariant). A
# `<placeholder>` token inside a Background step is a parse error, not a silent
# acceptance - this is the only parser-level rejection the interview names
# beyond the title rules (which live in `title_derivation_test.pyi`).
#
# These tests drive `beehave.gherkin.parse_feature` in-process; the SUT import
# lives in each body (deferred), so the `.pyi` does not import beehave.

# A minimal feature whose Background step carries a `<placeholder>` token.
BACKGROUND_WITH_PLACEHOLDER_FEATURE: str
# A minimal feature whose Background step is placeholder-free (the control).
BACKGROUND_CLEAN_FEATURE: str

def parse_feature_raises(feature_text: str) -> bool: ...
def test_background_step_with_placeholder_is_parse_error() -> None: ...
def test_background_step_without_placeholder_parses_cleanly() -> None: ...
