from unittest.mock import call

import pytest

from calcipy.tasks.test import default, step, watch, write_json

_COV = '--cov=calcipy --cov-report=term-missing'
_MARKERS = 'mark1 and not mark 2'
_FAILFIRST = '--failed-first --new-first --exitfirst -vv --no-cov'

# FIXME: pytest parametrize can have IDs!
#  https://github.com/pyinvoke/invocations/blob/8a277c304dd7aaad03888ee42d811c468e7fb37d/tests/checks.py#L49-L58
@pytest.mark.parametrize(
    ('task', 'kwargs', 'command'),
    [
        (default, {}, f'poetry run python -m pytest ./tests {_COV}'),
        (default, {'keyword': 'test'}, f'poetry run python -m pytest ./tests {_COV} -k "test"'),
        (default, {'marker': _MARKERS}, f'poetry run python -m pytest ./tests {_COV} -m "{_MARKERS}"'),
        (step, {'marker': _MARKERS}, f'poetry run python -m pytest ./tests {_FAILFIRST} -m "{_MARKERS}"'),
        (watch, {'marker': _MARKERS}, f'poetry run ptw . --now ./tests {_FAILFIRST} -m "{_MARKERS}"'),
    ],
    ids=[
        'Default test',
        'Default test with keyword',
        'Default test with marker',
        'step',
        'watch',
    ],
)
def test_test(ctx, task, kwargs, command):
    task(ctx, **kwargs)
    ctx.run.assert_called_once_with(command, echo=True, pty=True)


def test_write_json(ctx):
    write_json(ctx, out_dir='.cover')
    call_1 = 'poetry run coverage run --source=calcipy --module pytest ./tests --cov-report=html:.cover --html=.cover/test_report.html --self-contained-html'  # noqa: E501
    ctx.run.assert_has_calls([
        call(call_1, echo=True, pty=True),
        call('poetry run python -m coverage report --show-missing', echo=True, pty=True),
        call('poetry run python -m coverage html --directory=.cover', echo=True, pty=True),
        call('poetry run python -m coverage json', echo=True, pty=True),
    ])
