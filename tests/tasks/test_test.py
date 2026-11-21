import pytest
from corallium import file_helpers

from calcipy.tasks.executable_utils import python_dir, python_m
from calcipy.tasks.test import check, coverage, watch
from calcipy.tasks.test import pytest as task_pytest

_COV = (
    f'{python_m()} pytest ./tests --cov=mypkg --cov-branch --cov-report=term-missing '
    '--durations=25 --durations-min="0.1"'
)
_MARKERS = 'mark1 and not mark 2'
_PTW = f'{(python_dir() / "ptw").as_posix()} . --now ./tests --failed-first --new-first --exitfirst -vv --no-cov'
_COVERAGE = f'{python_m()} coverage'


@pytest.mark.parametrize(
    ('task', 'kwargs', 'config', 'commands'),
    [
        (task_pytest, {}, {}, [_COV]),
        (task_pytest, {'keyword': 'test'}, {}, [f'{_COV} -k "test"']),
        (task_pytest, {'marker': _MARKERS}, {}, [f'{_COV} -m "{_MARKERS}"']),
        (task_pytest, {'keyword': 'kw', 'marker': 'mk'}, {}, [f'{_COV} -k "kw" -m "mk"']),
        (task_pytest, {'min_cover': 80}, {}, [f'{_COV} --cov-fail-under=80']),
        (task_pytest, {}, {'min_cover': 75}, [f'{_COV} --cov-fail-under=75']),
        (task_pytest, {'min_cover': 80}, {'min_cover': 75}, [f'{_COV} --cov-fail-under=80']),
        (watch, {}, {}, [_PTW]),
        (watch, {'keyword': 'kw', 'marker': _MARKERS}, {}, [f'{_PTW} -k "kw" -m "{_MARKERS}"']),
        (
            coverage,
            {'out_dir': '.cover'},
            {},
            [
                f'{_COVERAGE} run --branch --source=mypkg --module pytest ./tests',
                f'{_COVERAGE} report --show-missing',
                f'{_COVERAGE} html --directory=.cover',
                f'{_COVERAGE} json',
            ],
        ),
        (
            coverage,
            {'min_cover': 90},
            {},
            [
                f'{_COVERAGE} run --branch --source=mypkg --module pytest ./tests',
                f'{_COVERAGE} report --show-missing --fail-under=90',
                f'{_COVERAGE} html --directory=releases/tests',
                f'{_COVERAGE} json',
            ],
        ),
        (
            coverage,
            {},
            {'out_dir': 'cov/html'},
            [
                f'{_COVERAGE} run --branch --source=mypkg --module pytest ./tests',
                f'{_COVERAGE} report --show-missing',
                f'{_COVERAGE} html --directory=cov/html',
                f'{_COVERAGE} json',
            ],
        ),
        (
            coverage,
            {},
            {'min_cover': 75, 'out_dir': '.cover'},
            [
                f'{_COVERAGE} run --branch --source=mypkg --module pytest ./tests',
                f'{_COVERAGE} report --show-missing --fail-under=75',
                f'{_COVERAGE} html --directory=.cover',
                f'{_COVERAGE} json',
            ],
        ),
        (
            coverage,
            {'min_cover': 90},
            {'min_cover': 75, 'out_dir': '.cover'},
            [
                f'{_COVERAGE} run --branch --source=mypkg --module pytest ./tests',
                f'{_COVERAGE} report --show-missing --fail-under=90',
                f'{_COVERAGE} html --directory=.cover',
                f'{_COVERAGE} json',
            ],
        ),
    ],
)
def test_test(ctx, tmp_project, task, kwargs, config, commands, assert_run_commands):
    if config:
        ctx.config['test'] = config

    task(ctx, **kwargs)

    assert_run_commands(ctx, commands)
    if task is coverage:
        html_dir = commands[2].split('--directory=')[1]
        assert (tmp_project / html_dir).is_dir()


@pytest.mark.parametrize(
    ('task', 'kwargs', 'commands'),
    [
        (task_pytest, {}, [_COV.replace('--cov=mypkg', '--cov=my_pkg')]),
        (
            coverage,
            {'out_dir': '.cover'},
            [
                f'{_COVERAGE} run --branch --source=my_pkg --module pytest ./tests',
                f'{_COVERAGE} report --show-missing',
                f'{_COVERAGE} html --directory=.cover',
                f'{_COVERAGE} json',
            ],
        ),
    ],
)
def test_test_dashed_project_name(ctx, tmp_project, task, kwargs, commands, assert_run_commands):
    (tmp_project / 'pyproject.toml').write_text('[project]\nname = "my-pkg"\n', encoding='utf-8')
    file_helpers.read_pyproject.cache_clear()
    file_helpers.read_package_name.cache_clear()

    task(ctx, **kwargs)

    assert_run_commands(ctx, commands)


@pytest.mark.parametrize(
    ('files', 'error'),
    [
        ({'test_a.py': 'def test_one(): ...\n', 'sub/test_b.py': 'def test_two(): ...\n'}, None),
        (
            {'test_a.py': 'def test_same(): ...\n', 'sub/test_b.py': 'def test_same(): ...\n'},
            "Duplicate test names found (['test_same']). See above for details.",
        ),
    ],
)
def test_test_check(ctx, tmp_project, files, error):
    for name, content in files.items():
        path = tmp_project / 'tests' / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    if error:
        with pytest.raises(RuntimeError) as exc_info:
            check(ctx)
        assert str(exc_info.value) == error
    else:
        check(ctx)

    ctx.run.assert_not_called()
