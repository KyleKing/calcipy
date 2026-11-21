from unittest.mock import Mock, call

import pytest
from beartype.typing import Any, Callable, List, cast

from calcipy.collection import Collection
from calcipy.tasks import all_tasks, lint, types
from calcipy.tasks.all_tasks import ns, with_progress


def _post(task_obj: Any) -> List[Any]:
    return task_obj.post


@pytest.mark.parametrize(
    ('name', 'steps', 'message', 'offset'),
    [
        (
            'main',
            ['fix', 'ty', 'mypy', 'pyright', 'coverage', 'write', 'build'],
            'Running tasks: fix, ty, mypy, pyright, coverage, write, build',
            0,
        ),
        ('release', ['write', 'lock', 'build', 'deploy'], 'Running tasks: write, lock, build, deploy', 1),
        (
            'other',
            ['pre_commit_', 'noxfile_', 'lock', 'collect_code_tags', 'check'],
            None,
            0,
        ),
    ],
)
def test_pipeline_post_tasks(ctx, monkeypatch, name, steps, message, offset):
    logger = Mock()
    monkeypatch.setattr('calcipy.tasks.all_tasks.LOGGER', logger)
    post = _post(ns.tasks[name])

    assert len(post) == 1 + 2 * len(steps)
    assert [t.name[: len(s)] for t, s in zip(post[2::2], steps, strict=True)] == steps

    for task in [post[0], *post[1::2]]:
        task.body.__wrapped__(ctx)
    total = len(steps) + offset
    progress = [call.text('Progress', is_header=True, index=idx + 1 + offset, total=total) for idx in range(len(steps))]
    if message:
        assert logger.mock_calls == [call.text(message, is_header=True), *progress]
    else:
        assert logger.mock_calls[1:] == progress
    ctx.run.assert_not_called()

    getattr(all_tasks, name)(ctx)

    assert ctx.run.call_count == (1 if name == 'release' else 0)


@pytest.mark.parametrize(
    ('namespace', 'task_name', 'post_names'),
    [('cl', 'bump', ['write']), ('pack', 'sync-pyproject-versions', ['lock'])],
)
def test_namespace_post_tasks(namespace, task_name, post_names):
    post = _post(cast(Collection, ns.collections[namespace]).tasks[task_name])
    assert [t.name for t in post] == post_names


def test_with_progress_orders_tasks(ctx, monkeypatch):
    logger = Mock()
    monkeypatch.setattr('calcipy.tasks.all_tasks.LOGGER', logger)

    tasks = with_progress([lint.fix, types.mypy], offset=2)

    assert [getattr(t, 'name', None) for t in tasks] == [None, None, 'fix', None, 'mypy']
    for task in [tasks[0], *tasks[1::2]]:
        cast(Callable[..., None], task)(ctx)
    assert logger.mock_calls == [
        call.text('Running tasks: fix, mypy', is_header=True),
        call.text('Progress', is_header=True, index=3, total=4),
        call.text('Progress', is_header=True, index=4, total=4),
    ]
