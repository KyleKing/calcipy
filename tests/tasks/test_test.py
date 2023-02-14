import pytest
from calcipy.tasks.test import default

# FIXME: pytest parametrize can have IDs?
#  https://github.com/pyinvoke/invocations/blob/8a277c304dd7aaad03888ee42d811c468e7fb37d/tests/checks.py#L49-L58
@pytest.mark.parametrize(
    'kwargs,command',
    [
        ({}, 'poetry run python -m pytest ./tests'),
        ({'keyword': 'test'}, 'poetry run python -m pytest ./tests -k "test"'),
        ({'marker': 'mark1 and not mark 2'}, 'poetry run python -m pytest ./tests -m "mark1 and not mark 2"'),
    ],
    ids=[
        'Default test',
        'Default test with keyword',
        'Default test with marker',
    ],
)
def test_test(ctx, kwargs, command):
    default(ctx, **kwargs)
    ctx.run.assert_called_once_with(command, echo=True, pty=True)
