from pathlib import Path
from unittest.mock import call, patch

import pytest

from calcipy.collection import GlobalTaskOptions
from calcipy.tasks.executable_utils import python_m
from calcipy.tasks.lint import ALL_PRE_COMMIT_HOOK_STAGES, check, fix, pre_commit, watch


@pytest.mark.parametrize(
    ('task', 'kwargs', 'commands'),
    [
        (check, {}, [f'{python_m()} ruff check "calcipy" ./tests']),
        (fix, {}, [f'{python_m()} ruff check "calcipy" ./tests --fix']),
        (fix, {'unsafe': True}, [f'{python_m()} ruff check "calcipy" ./tests --fix --unsafe-fixes']),
        (watch, {}, [f'{python_m()} ruff check "calcipy" ./tests --watch']),
        (
            pre_commit,
            {},
            [
                call('which prek', warn=True, hide=True),
                'prek install',
                'prek autoupdate',
                'prek run --all-files ' + ' '.join(f'--hook-stage {stg}' for stg in ALL_PRE_COMMIT_HOOK_STAGES),
            ],
        ),
    ],
)
def test_lint(ctx, task, kwargs, commands, assert_run_commands):
    task(ctx, **kwargs)

    assert_run_commands(ctx, commands)


def test_lint_check_with_file_args(ctx):
    gto = GlobalTaskOptions(file_args=[Path('a.py'), Path('b.py')])
    ctx.config.gto = gto

    check(ctx)

    ctx.run.assert_called_once_with(f'{python_m()} ruff check "a.py" "b.py"')


def test_lint_check_src_layout(ctx, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / 'src' / 'mypkg').mkdir(parents=True)

    with patch('calcipy.tasks.lint.read_package_name', return_value='mypkg'):
        check(ctx)

    ctx.run.assert_called_once_with(f'{python_m()} ruff check "src/mypkg" ./tests')
