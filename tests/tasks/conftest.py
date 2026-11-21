from unittest.mock import call

import pytest

from calcipy.tasks.executable_utils import _EXECUTABLE_CACHE


@pytest.fixture(autouse=True)
def _clear_executable_cache():
    _EXECUTABLE_CACHE.clear()
    yield
    _EXECUTABLE_CACHE.clear()


@pytest.fixture
def assert_run_commands():
    def _check(ctx, commands):
        assert ctx.run.call_args_list == [call(cmd) if isinstance(cmd, str) else cmd for cmd in commands]

    return _check
