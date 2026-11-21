import sys
from base64 import b64encode
from pathlib import Path
from unittest.mock import Mock

import pytest

from calcipy import cli
from calcipy.cli import start_program, task
from calcipy.collection import Collection, GlobalTaskOptions
from calcipy.tasks import nox


def test_task_decorator_records_invoke_arguments():
    @task
    def bare(ctx, *, value=0):
        return (ctx, value)

    @task('positional', default=True, help={'value': 'A value'}, post=['after'])
    def configured(ctx):
        return ctx

    assert bare('ctx', value=2) == ('ctx', 2)
    assert bare.__wrapped__.__name__ == 'bare'  # type: ignore[attr-defined]  # ty: ignore[unresolved-attribute]
    assert (bare.dev_args, bare.dev_kwargs, bare.help) == ((), {}, {})  # type: ignore[attr-defined]  # ty: ignore[unresolved-attribute]
    assert configured('ctx') == 'ctx'
    assert configured.dev_args == ('positional',)  # pyright: ignore[reportFunctionMemberAccess]  # ty: ignore[unresolved-attribute]
    assert configured.dev_kwargs == {'default': True, 'post': ['after']}  # pyright: ignore[reportFunctionMemberAccess]  # ty: ignore[unresolved-attribute]
    assert configured.help == {'value': 'A value'}  # pyright: ignore[reportFunctionMemberAccess]  # ty: ignore[unresolved-attribute]


@pytest.mark.parametrize(
    ('extra_kwargs', 'suffix'),
    [({}, ''), ({'value': 5}, '_' + b64encode(b"{'value': 5}").decode().rstrip('='))],
)
def test_task_with_kwargs(extra_kwargs, suffix):
    @task
    def partial_task(ctx, *, value=0):
        return (ctx, value)

    bound = partial_task.with_kwargs(**extra_kwargs)  # type: ignore[attr-defined]  # ty: ignore[unresolved-attribute]

    assert bound('ctx') == ('ctx', extra_kwargs.get('value', 0))
    assert bound.__name__ == f'partial_task{suffix}'
    assert bound.dev_kwargs == {}


def test_start_program_parses_global_options(tmp_path, monkeypatch):
    (tmp_path / 'a.py').write_text('')
    (tmp_path / 'sub').mkdir()
    monkeypatch.chdir(tmp_path)
    argv = ['calcipy', 'a.py', '-vv', '--keep-going', '--working-dir', 'sub', 'lint.check', '--target', 'a.py']
    monkeypatch.setattr(sys, 'argv', argv)
    program = Mock()
    monkeypatch.setattr(cli, '_CalcipyProgram', program)

    start_program('pkg', '1.2.3', module=nox)

    assert sys.argv == ['calcipy', 'lint.check', '--target', 'a.py']
    kwargs = program.call_args.kwargs
    assert (kwargs['name'], kwargs['version']) == ('pkg', '1.2.3')
    assert kwargs['namespace'].task_names == {'noxfile': []}
    assert kwargs['config_class'].gto == GlobalTaskOptions(
        working_dir=(tmp_path / 'sub').resolve(),
        file_args=[tmp_path / 'a.py'],
        verbose=2,
        keep_going=True,
    )
    program.return_value.run.assert_called_once_with()


@pytest.mark.parametrize(('flag', 'verbose'), [('-v', 1), ('-vvv', 3), ('--verbose', 1)])
def test_start_program_verbosity(monkeypatch, flag, verbose):
    collection = Collection()
    monkeypatch.setattr(sys, 'argv', ['calcipy', flag])
    program = Mock()
    monkeypatch.setattr(cli, '_CalcipyProgram', program)

    start_program('pkg', '1.2.3', collection=collection)

    gto = program.call_args.kwargs['config_class'].gto
    assert (gto.verbose, gto.keep_going, gto.file_args, gto.working_dir) == (verbose, False, [], Path.cwd())
    assert program.call_args.kwargs['namespace'] is collection


def test_start_program_rejects_module_and_collection(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['calcipy'])
    monkeypatch.setattr(cli, '_CalcipyProgram', Mock())

    with pytest.raises(ValueError, match='Only one of collection or module can be specified'):
        start_program('pkg', '1.2.3', module=nox, collection=Collection.from_module(nox))
