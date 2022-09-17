"""Test dot_dict."""

import arrow
import pytest

from calcipy.dot_dict import ddict


# TODO: Convert to hypothesis test!
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
