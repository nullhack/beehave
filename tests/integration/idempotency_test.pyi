# Integration contract for `generate` idempotency at the generation unit.
#
# `generate` re-run on a feature whose `*_test.py` already carries consumer
# bodies preserves those bodies - the `.py` is never rewritten (interview L2
# Modifiability / idempotency). This is the cycle's defining property and
# the protection for the consumer-authored seam. Under v3.0.0 there is no
# `.pyi` emission; adding a scenario to the feature leaves the existing
# `.py` byte-identical (consumer reconciles via `beehave check`).
#
# These tests drive `generate` in-process; the SUT imports live in each body
# (deferred).

# A minimal feature used as the idempotency input.
BASE_FEATURE: str
# The same feature with one additional scenario.
EXTENDED_FEATURE: str

def emit_test_py_for(feature_text: str) -> str: ...
def regenerate_over_body(feature_text: str, existing_py_body: str) -> str: ...
def test_regenerate_preserves_existing_consumer_py_body() -> None: ...
def test_regenerate_does_not_emit_py_when_py_present() -> None: ...
def test_regenerate_is_noop_when_feature_gains_scenario() -> None: ...
