"""Test dot_dict."""

from datetime import datetime

from calcipy.dot_dict import ddict


def test_ddict():
    """Test ddict."""
    now = datetime.now()

    result = ddict(int=1, number=-1.23, date=now, unicode='✓', is_bool=False)

    assert isinstance(result, dict)
    assert result.int == 1
    assert result['int'] == 1
    assert result.number == -1.23
    assert result['number'] == -1.23
    assert result.date == now
    assert result['date'] == now
    assert result.unicode == '✓'
    assert result['unicode'] == '✓'
    assert not result.is_bool
    assert not result['is_bool']
