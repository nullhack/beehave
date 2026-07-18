# Integration contract for the generate -> check round-trip.
#
# `generate` emits a `.pyi` (always) and a `.py` skeleton (when absent);
# `check` walks the emitted `.py` body's `with step(...)` blocks against the
# parsed `.feature` and enforces structural binding. The round-trip is the
# load-bearing claim that generator and checker agree on the contract -
# a freshly generated body must pass `check`, and only consumer edits that
# change the structural binding fields (keyword/text/placeholder-name-set)
# may fail it.
#
# These tests drive the generate+check module path in-process (no subprocess);
# the SUT imports live in each body (deferred), so the `.pyi` does not
# import beehave.

# A minimal feature used as the round-trip input.
ROUND_TRIP_FEATURE: str

def emit_test_py_for(feature_text: str) -> str: ...
def check_passes_for(feature_text: str, test_py_text: str) -> bool: ...
def test_check_passes_on_freshly_generated_py() -> None: ...
def test_check_fails_after_consumer_edits_step_text() -> None: ...
def test_check_fails_after_consumer_removes_step_block() -> None: ...
def test_check_passes_after_consumer_adds_body_content() -> None: ...
