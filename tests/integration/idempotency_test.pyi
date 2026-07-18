# Integration contract for `generate` idempotency at the generation unit.
#
# `generate` re-run on a feature whose `*_test.py` already carries consumer
# bodies preserves those bodies - only the `.pyi` is rewritten (interview L2
# Modifiability / idempotency). This is the cycle's defining property and
# the protection for the consumer-authored seam.
#
# These tests drive `generate` in-process; the SUT imports live in each body
# (deferred), so the `.pyi` does not import beehave.

# A minimal feature used as the idempotency input.
BASE_FEATURE: str
# The same feature with one additional scenario (drives `.pyi` re-emission).
EXTENDED_FEATURE: str

def emit_test_py_for(feature_text: str) -> str: ...
def emit_test_pyi_for(feature_text: str) -> str: ...
def regenerate_over_body(feature_text: str, existing_py_body: str) -> str: ...
def test_regenerate_preserves_existing_consumer_py_body() -> None: ...
def test_regenerate_does_not_emit_py_when_py_present() -> None: ...
def test_regenerate_rewrites_pyi_when_feature_gains_scenario() -> None: ...
