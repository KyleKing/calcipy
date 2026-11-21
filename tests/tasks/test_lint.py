import json
from pathlib import Path
from unittest.mock import call

import pytest
from corallium import file_helpers
from corallium.shell import capture_shell

from calcipy.collection import GlobalTaskOptions
from calcipy.tasks.executable_utils import python_m
from calcipy.tasks.lint import PRE_COMMIT_HOOK_STAGES, check, fix, pre_commit, prose, slop_export, watch

_RUFF = f'{python_m()} ruff check'
_PREK_RUNS = [f'prek run --all-files --hook-stage {stg}' for stg in PRE_COMMIT_HOOK_STAGES]


@pytest.mark.parametrize(
    ('task', 'kwargs', 'commands'),
    [
        (check, {}, [f'{_RUFF} "calcipy" ./tests']),
        (fix, {}, [f'{_RUFF} "calcipy" ./tests --fix']),
        (fix, {'unsafe': True}, [f'{_RUFF} "calcipy" ./tests --fix --unsafe-fixes']),
        (watch, {}, [f'{_RUFF} "calcipy" ./tests --watch']),
        (
            pre_commit,
            {},
            [call('which prek', warn=True, hide=True), 'prek install', 'prek autoupdate', *_PREK_RUNS],
        ),
        (pre_commit, {'no_update': True}, [call('which prek', warn=True, hide=True), 'prek install', *_PREK_RUNS]),
        (prose, {}, [call('which vale', warn=True, hide=True), 'vale sync', 'vale .']),
        (prose, {'target': 'docs', 'no_sync': True}, [call('which vale', warn=True, hide=True), 'vale docs']),
        (
            prose,
            {'target': 'docs .github', 'glob': '*.md', 'no_sync': True},
            [call('which vale', warn=True, hide=True), "vale --glob='*.md' docs .github"],
        ),
        (
            prose,
            {'glob': '*.md'},
            [call('which vale', warn=True, hide=True), 'vale sync', "vale --glob='*.md' ."],
        ),
    ],
)
def test_lint(ctx, task, kwargs, commands, assert_run_commands):
    task(ctx, **kwargs)

    assert_run_commands(ctx, commands)


@pytest.mark.parametrize(
    ('name', 'dirs', 'file_args', 'target'),
    [
        ('mypkg', ['src/mypkg', 'mypkg'], [], '"src/mypkg" ./tests'),
        ('mypkg', ['mypkg'], [], '"mypkg" ./tests'),
        ('mypkg', [], [], '. ./tests'),
        ('mypkg', ['mypkg'], [Path('a.py'), Path('b c.py')], '"a.py" "b c.py"'),
        ('my-pkg', ['src/my_pkg'], [], '"src/my_pkg" ./tests'),
        ('my-pkg', ['my_pkg'], [], '"my_pkg" ./tests'),
    ],
    ids=['src-layout', 'flat-layout', 'no-package-dir', 'file-args', 'dashed-src-layout', 'dashed-flat-layout'],
)
def test_lint_check_target(ctx, tmp_project, name, dirs, file_args, target):
    (tmp_project / 'pyproject.toml').write_text(f'[project]\nname = "{name}"\n', encoding='utf-8')
    file_helpers.read_pyproject.cache_clear()
    file_helpers.read_package_name.cache_clear()
    for dir_name in dirs:
        (tmp_project / dir_name).mkdir(parents=True)
    if file_args:
        ctx.config.gto = GlobalTaskOptions(file_args=file_args)

    check(ctx)

    ctx.run.assert_called_once_with(f'{_RUFF} {target}')


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
    assert [(Path(r['id']).name, r['source'], r['model']) for r in records] == [('doc.md', 'repo', 'repo')]
    ctx.run.assert_not_called()
