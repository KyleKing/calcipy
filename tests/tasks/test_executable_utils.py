from unittest.mock import Mock, call

import pytest
from beartype.typing import cast
from invoke.context import MockContext
from invoke.runners import Result

from calcipy.tasks import lint, types
from calcipy.tasks.executable_utils import (
    _EXECUTABLE_CACHE,
    PRE_COMMIT_MESSAGE,
    PYRIGHT_MESSAGE,
    VALE_MESSAGE,
    check_installed,
)


@pytest.mark.parametrize(
    ('task', 'executable', 'message'),
    [
        (lint.pre_commit, 'prek', PRE_COMMIT_MESSAGE),
        (lint.prose, 'vale', VALE_MESSAGE),
        (types.pyright, 'pyright', PYRIGHT_MESSAGE),
    ],
)
def test_task_stops_when_executable_missing(task, executable, message):
    ctx = MockContext(run=Result(exited=1))

    with pytest.raises(RuntimeError) as exc_info:
        task(ctx)

    assert str(exc_info.value) == message
    assert cast(Mock, ctx.run).call_args_list == [call(f'which {executable}', warn=True, hide=True)]


_NOT_CACHED = object()


@pytest.mark.parametrize(
    ('cached', 'raises', 'lookups'),
    [(_NOT_CACHED, False, 1), (Result(exited=0), False, 0), (Result(exited=1), True, 0), (None, True, 0)],
)
def test_check_installed_caches_lookup(ctx, cached, raises, lookups):
    if cached is not _NOT_CACHED:
        _EXECUTABLE_CACHE['tool'] = cached

    for _ in range(2):
        if raises:
            with pytest.raises(RuntimeError, match=r'^missing$'):
                check_installed(ctx, executable='tool', message='missing')
        else:
            check_installed(ctx, executable='tool', message='missing')

    assert ctx.run.call_args_list == [call('which tool', warn=True, hide=True)] * lookups
