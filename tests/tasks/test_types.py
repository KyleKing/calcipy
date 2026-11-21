from unittest.mock import call

import pytest

from calcipy.tasks.executable_utils import python_m
from calcipy.tasks.types import mypy, pyright, ty


@pytest.mark.parametrize(
    ('task', 'dirs', 'commands'),
    [
        (pyright, [], [call('which pyright', warn=True, hide=True), 'pyright']),
        (mypy, [], [f'{python_m()} mypy']),
        (ty, ['mypkg'], ['ty check "mypkg" tests']),
        (ty, ['src/mypkg', 'mypkg'], ['ty check "src/mypkg" tests']),
        (ty, [], ['ty check . tests']),
    ],
    ids=['pyright', 'mypy', 'ty-flat-layout', 'ty-src-layout', 'ty-no-package-dir'],
)
def test_types(ctx, tmp_project, task, dirs, commands, assert_run_commands):
    for dir_name in dirs:
        (tmp_project / dir_name).mkdir(parents=True)

    task(ctx)

    assert_run_commands(ctx, commands)
