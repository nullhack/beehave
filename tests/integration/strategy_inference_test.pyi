# Integration contract for Examples-table -> Hypothesis strategy -> `.pyi` type.
#
# The generation rule (interview L1): for each Examples column, the strategy is
# inferred from cell values across all rows - all-parseable int -> int,
# all-parseable float -> float, all-parseable bool -> bool, otherwise -> str.
# When a Scenario has no Examples table, placeholders default to `str`
# (decision Q4 - simplest sound default; matches the "otherwise -> str" branch).
#
# These tests drive `beehave.gherkin.parse_feature` + `beehave.generate`'s
# emission path in-process; the SUT imports live in each body (deferred), so
# the `.pyi` does not import beehave.

# Minimal feature snippets exercising each strategy branch.
INT_COLUMN_FEATURE: str
FLOAT_COLUMN_FEATURE: str
BOOL_COLUMN_FEATURE: str
MIXED_COLUMN_FEATURE: str
TEXT_COLUMN_FEATURE: str
NO_EXAMPLES_FEATURE: str

def emitted_function_signature(feature_text: str, scenario_slug: str) -> str: ...
def test_all_int_column_infers_int_parameter() -> None: ...
def test_all_float_column_infers_float_parameter() -> None: ...
def test_all_bool_column_infers_bool_parameter() -> None: ...
def test_mixed_type_column_infers_str_parameter() -> None: ...
def test_text_column_infers_str_parameter() -> None: ...
def test_no_examples_table_infers_str_parameter() -> None: ...
