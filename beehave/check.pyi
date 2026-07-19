# v2.3 signature check: regenerates expected `def test_<slug>(...) -> None: ...`
# lines from the feature source and verifies each appears in `stub_text`
# (the concatenated content of `tests/features/*_test.pyi`). Returns True iff
# every scenario signature is present; False on any missing signature (stale
# `.pyi`). Does NOT inspect the `.py` body — step/parametrize verification is
# the runtime `step()` CM's job (Mode B). The CLI additionally runs
# `mypy.stubtest` on the consumer test modules for `.py` ↔ `.pyi` drift.
def check(feature_text: str, stub_text: str) -> bool: ...
