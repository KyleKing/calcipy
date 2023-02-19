import arrow
import pytest
from hypothesis import given
from hypothesis import strategies as st

from calcipy.dot_dict import ddict


# PLANNED: Convert to hypothesis test!
@pytest.mark.parametrize(
    ('key', 'value'), [
        ('int', 1),
        ('number', -1.23),
        ('unicode', '✓'),
        ('is_bool', False),
        ('datetime', arrow.now()),
    ],
)
def test_ddict(key, value):
    """Test ddict."""
    result = ddict(**{key: value})

    assert getattr(result, key) == value
    assert result[key] == value
    assert isinstance(result, dict)
    assert result.get(f'--{key}--') is None


_ST_ANY = st.booleans() | st.binary() | st.integers() | st.text()
"""Broadest swatch of strategies for data input testing of dotdict."""


@given(
    key=st.text(),
    value=(_ST_ANY | st.dictionaries(keys=_ST_ANY, values=_ST_ANY, max_size=10)),
)
def test_ddict_with_hypothesis(key, value):
    """Test ddict."""
    result = ddict(**{key: value})

    assert getattr(result, key) == value
    assert result[key] == value
    assert isinstance(result, dict)
    assert result.get(f'--{key}--') is None
