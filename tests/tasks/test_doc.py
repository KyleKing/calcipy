import pytest

from calcipy.tasks.doc import _get_doc_dir, build, deploy, get_out_dir
from calcipy.tasks.executable_utils import python_m, resolve_python


@pytest.mark.parametrize(
    ('task', 'kwargs', 'commands'),
    [
        (
            build,
            {},
            [
                f'{resolve_python()} {_get_doc_dir()}/gen_ref_nav.py',
                f'{python_m()} zensical build',
            ],
        ),
        (
            deploy,
            {},
            [f'{python_m()} ghp_import --no-jekyll --push --force --message "Deployed docs" {get_out_dir()}'],
        ),
    ],
)
def test_doc(ctx, task, kwargs, commands, assert_run_commands):
    task(ctx, **kwargs)

    assert_run_commands(ctx, commands)
