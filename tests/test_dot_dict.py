from hypothesis import given
from hypothesis import strategies as st

from calcipy.dot_dict import ddict

_ST_ANY = st.booleans() | st.binary() | st.integers() | st.floats(allow_nan=False) | st.text() | st.datetimes()
"""Broadest set of strategies for data input testing of dot_dict."""


@given(
    key=st.text().filter(lambda k: not (k.startswith('__') and k.endswith('__'))),
    value=(_ST_ANY | st.dictionaries(keys=_ST_ANY, values=_ST_ANY, max_size=10)),
)
def test_ddict(key, value):
    result = ddict(**{key: value})

    assert getattr(result, key) == value
    assert result[key] == value
    assert dict(result) == {key: value}
    assert result.get(f'--{key}--') is None
