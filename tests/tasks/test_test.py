from unittest.mock import call

import pytest

from calcipy.tasks.executable_utils import python_dir, python_m
from calcipy.tasks.test import check, coverage, watch
from calcipy.tasks.test import pytest as task_pytest

_COV = '--cov=calcipy --cov-branch --cov-report=term-missing --durations=25 --durations-min="0.1"'
_MARKERS = 'mark1 and not mark 2'
_FAILFIRST = '--failed-first --new-first --exitfirst -vv --no-cov'


@pytest.mark.parametrize(
    ('task', 'kwargs', 'commands'),
    [
        (task_pytest, {}, [f'{python_m()} pytest ./tests {_COV}']),
        (task_pytest, {'keyword': 'test'}, [f'{python_m()} pytest ./tests {_COV} -k "test"']),
        (task_pytest, {'marker': _MARKERS}, [f'{python_m()} pytest ./tests {_COV} -m "{_MARKERS}"']),
        (
            watch,
            {'marker': _MARKERS},
            [f'{(python_dir() / "ptw").as_posix()} . --now ./tests {_FAILFIRST} -m "{_MARKERS}"'],
        ),
        (
            coverage,
            {'out_dir': '.cover'},
            [
                f'{python_m()} coverage run --branch --source=calcipy --module pytest ./tests',
                call(f'{python_m()} coverage report --show-missing'),
                call(f'{python_m()} coverage html --directory=.cover'),
                call(f'{python_m()} coverage json'),
            ],
        ),
    ],
    ids=[
        'Default test',
        'Default test with keyword',
        'Default test with marker',
        'watch',
        'coverage',
    ],
)
def test_test(ctx, task, kwargs, commands):
    task(ctx, **kwargs)

    ctx.run.assert_has_calls([call(cmd) if isinstance(cmd, str) else cmd for cmd in commands])


def test_test_check(ctx):
    with pytest.raises(RuntimeError, match=r'Duplicate test names.+test_intentional_duplicate.+'):
        check(ctx)
