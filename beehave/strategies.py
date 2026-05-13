from hypothesis import strategies as st


def resolve_strategy(name, module, examples=None):
    obj = getattr(module, name, None)
    if obj is not None and hasattr(obj, "filter") and hasattr(obj, "map"):
        return obj
    if examples and name in examples:
        return st.from_type(type(examples[name]))
    return st.integers()
