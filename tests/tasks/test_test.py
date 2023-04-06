from unittest.mock import call

import pytest

from calcipy.tasks.test import check, coverage, step, watch
from calcipy.tasks.test import pytest as task_pytest

_COV = '--cov=calcipy --cov-report=term-missing'
_MARKERS = 'mark1 and not mark 2'
_FAILFIRST = '--failed-first --new-first --exitfirst -vv --no-cov'


# TODO: Is there an easier way to maintain pytest parameter IDs?
#  https://github.com/pyinvoke/invocations/blob/8a277c304dd7aaad03888ee42d811c468e7fb37d/tests/checks.py#L49-L58
@pytest.mark.parametrize(
    ('task', 'kwargs', 'commands'),
    [
        (task_pytest, {}, [f'poetry run python -m pytest ./tests {_COV}']),
        (task_pytest, {'keyword': 'test'}, [f'poetry run python -m pytest ./tests {_COV} -k "test"']),
        (task_pytest, {'marker': _MARKERS}, [f'poetry run python -m pytest ./tests {_COV} -m "{_MARKERS}"']),
        (step, {'marker': _MARKERS}, [f'poetry run python -m pytest ./tests {_FAILFIRST} -m "{_MARKERS}"']),
        (watch, {'marker': _MARKERS}, [f'poetry run ptw . --now ./tests {_FAILFIRST} -m "{_MARKERS}"']),
        (coverage, {'out_dir': '.cover'}, [
            'poetry run coverage run --source=calcipy --module pytest ./tests',
            call('poetry run python -m coverage report --show-missing'),
            call('poetry run python -m coverage html --directory=.cover'),
            call('poetry run python -m coverage json'),
        ]),
    ],
    ids=[
        'Default test',
        'Default test with keyword',
        'Default test with marker',
        'step',
        'watch',
        'coverage',
    ],
)
def test_test(ctx, task, kwargs, commands):
    task(ctx, **kwargs)

    ctx.run.assert_has_calls([
        call(cmd) if isinstance(cmd, str) else cmd
        for cmd in commands
    ])


def test_test_check(ctx):
    with pytest.raises(RuntimeError, match=r'Duplicate test names.+test_intentional_duplicate.+'):
        check(ctx)
