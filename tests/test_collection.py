import logging
from pathlib import Path
from unittest.mock import Mock

import pytest
from beartype.typing import Any, List, cast
from invoke.tasks import Task

from calcipy.cli import task
from calcipy.collection import Collection, GlobalTaskOptions, _build_task
from calcipy.tasks import nox


@pytest.mark.parametrize('verbose', [-1, 4, 99])
def test_global_task_options_invalid_verbose(verbose):
    with pytest.raises(ValueError, match=r'verbose must be one of: \[3, 2, 1, 0\]'):
        GlobalTaskOptions(verbose=verbose)


def test_from_module_builds_deferred_tasks():
    collection = Collection.from_module(nox)

    assert collection.task_names == {'noxfile': []}
    assert collection.default == 'noxfile'
    assert isinstance(collection.tasks['noxfile'], Task)


def test_build_task_returns_invoke_tasks_unchanged():
    def plain(ctx):
        return ctx

    existing: Task[Any] = Task(plain)

    assert _build_task(existing) is existing


@pytest.fixture
def configure_logger(monkeypatch):
    mock = Mock()
    monkeypatch.setattr('calcipy.collection.configure_logger', mock)
    return mock


def _build(body, **task_kwargs):
    @task(**task_kwargs)
    def sample(ctx, *, value=1):
        """Sample task."""
        return body(value)

    return _build_task(sample)


@pytest.mark.parametrize(('verbose', 'log_level'), [(0, logging.WARNING), (2, logging.DEBUG), (3, logging.NOTSET)])
@pytest.mark.parametrize('show_task_info', [True, False])
def test_built_task_runs_in_working_dir(
    ctx, tmp_path, monkeypatch, configure_logger, verbose, log_level, show_task_info
):
    monkeypatch.chdir(tmp_path)
    working_dir = tmp_path / 'wd'
    working_dir.mkdir()
    ctx.config.gto = GlobalTaskOptions(working_dir=working_dir, verbose=verbose)
    built = _build(lambda value: (Path.cwd(), value), show_task_info=show_task_info)

    assert built.name == 'sample'
    assert built(ctx, value=3) == (working_dir, 3)
    configure_logger.assert_called_once_with(log_level=log_level)


def _fail(value):
    msg = f'failed {value}'
    raise RuntimeError(msg)


def _print(value):
    print(f'stdout {value}')  # noqa: T201
    return value


@pytest.mark.parametrize(
    ('gto', 'body', 'expected', 'stdout'),
    [
        (None, _print, 1, 'stdout 1\n'),
        (GlobalTaskOptions(capture_output=True), _print, 1, ''),
        (GlobalTaskOptions(keep_going=True), _fail, None, None),
        (GlobalTaskOptions(), _fail, RuntimeError, ''),
    ],
    ids=['defaults', 'capture-output', 'keep-going', 'raises'],
)
def test_built_task_global_options(ctx, capsys, configure_logger, gto, body, expected, stdout):
    if gto:
        ctx.config.gto = gto
    built = _build(body, show_task_info=False)

    if expected is RuntimeError:
        with pytest.raises(RuntimeError, match='failed 1'):
            built(ctx)
    else:
        assert built(ctx) == expected
    out = capsys.readouterr().out
    if stdout is None:
        assert '[EXCEPTION] Task Failed' in out
    else:
        assert out == stdout
    assert ctx.config.gto == (gto or GlobalTaskOptions())


def test_built_task_builds_pre_and_post():
    @task()
    def before(ctx):
        """Before."""

    @task()
    def after(ctx):
        """After."""

    built = _build(lambda value: value, pre=[before], post=[after])

    assert [t.name for t in cast(List[Task[Any]], built.pre)] == ['before']
    assert [t.name for t in cast(List[Task[Any]], built.post)] == ['after']


@pytest.mark.parametrize(
    ('task_help', 'expected'),
    [
        ({}, {}),
        ({'value': 'The value'}, {'value': 'The value'}),
    ],
)
def test_built_task_keeps_help(task_help, expected):
    built = _build(lambda value: value, help=task_help)

    assert built.help == expected
