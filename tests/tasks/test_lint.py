import json
from pathlib import Path
from unittest.mock import call, patch

import pytest
from corallium.shell import capture_shell

from calcipy.collection import GlobalTaskOptions
from calcipy.tasks.executable_utils import _EXECUTABLE_CACHE, python_m
from calcipy.tasks.lint import PRE_COMMIT_HOOK_STAGES, check, fix, pre_commit, prose, slop_export, watch


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
                *[f'prek run --all-files --hook-stage {stg}' for stg in PRE_COMMIT_HOOK_STAGES],
            ],
        ),
        (
            prose,
            {},
            [
                call('which vale', warn=True, hide=True),
                'vale sync',
                'vale .',
            ],
        ),
        (
            prose,
            {'target': 'docs', 'no_sync': True},
            [
                call('which vale', warn=True, hide=True),
                'vale docs',
            ],
        ),
        (
            prose,
            {'target': 'docs .github', 'glob': '*.md', 'no_sync': True},
            [
                call('which vale', warn=True, hide=True),
                "vale --glob='*.md' docs .github",
            ],
        ),
    ],
)
def test_lint(ctx, task, kwargs, commands, assert_run_commands):
    _EXECUTABLE_CACHE.pop('vale', None)

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


def test_lint_slop_export(ctx, tmp_path):
    (tmp_path / 'doc.md').write_text(' '.join(['word'] * 200))
    vendored = tmp_path / '.venv' / 'pkg-1.0.dist-info' / 'licenses'
    vendored.mkdir(parents=True)
    (vendored / 'LICENSE.md').write_text(' '.join(['license'] * 200))
    capture_shell('git init', cwd=tmp_path)
    capture_shell('git add doc.md', cwd=tmp_path)
    output_dir = tmp_path / 'out'

    slop_export(ctx, target=str(tmp_path), output_dir=str(output_dir), source='repo')

    records = [json.loads(line) for line in (output_dir / 'generated_repo.jsonl').read_text().splitlines()]
    assert [Path(r['id']).name for r in records] == ['doc.md']
    ctx.run.assert_not_called()
