"""Testing of schemas.

USAGE:
    pytest tests/test_schemas.py
"""

from projectcard.io import _change_keys


def test_change_keys():
    _orig_dict = {"a": 1, "b": 2, "ab": [{"a": 1, "c": 2}], "abc": {"b": 1, "bc": 2}}
    _expected_dict = {
        "A": 1,
        "B": 2,
        "ab": [{"A": 1, "c": 2}],
        "abc": {"B": 1, "bc": 2},
    }
    _changed_dict = _change_keys(_orig_dict)
    assert _expected_dict == _changed_dict
