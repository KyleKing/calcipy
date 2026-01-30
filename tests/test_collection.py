import pytest

from calcipy.collection import GlobalTaskOptions


def test_global_task_options_invalid_verbose():
    with pytest.raises(ValueError, match='verbose must be one of'):
        GlobalTaskOptions(verbose=99)
