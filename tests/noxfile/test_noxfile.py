from unittest.mock import Mock, call

import pytest
from nox.sessions import Session

from calcipy.noxfile import _noxfile
from calcipy.noxfile._noxfile import _get_pythons, _has_ci_group


@pytest.mark.parametrize(
    ('pyproject_data', 'expected'),
    [
        ({'dependency-groups': {'ci': ['hypothesis[cli] >=6.112.4', 'pytest-asyncio >=0.24.0']}}, True),
        ({'dependency-groups': {'ci': []}}, False),
        ({'dependency-groups': {'docs': ['mkdocs >=1.6.1']}}, False),
        ({}, False),
    ],
)
def test_has_ci_group(pyproject_data, expected):
    assert _has_ci_group(pyproject_data) is expected


@pytest.mark.parametrize(
    ('pyproject_toml', 'sync_args'),
    [
        ('[dependency-groups]\nci = ["pytest"]\n', ('uv', 'sync', '--group=ci', '--no-default-groups')),
        ('[project]\nname = "mypkg"\n', ('uv', 'sync', '--all-extras')),
    ],
)
def test_tests_session_installs_then_runs_pytest(tmp_project, pyproject_toml, sync_args):
    (tmp_project / 'pyproject.toml').write_text(pyproject_toml)
    session = Mock(spec=Session)
    session.virtualenv.location = '/venv'

    _noxfile.tests(session)

    assert session.mock_calls == [
        call.run_install(*sync_args, env={'UV_PROJECT_ENVIRONMENT': '/venv'}),
        call.run('pytest', './tests', stdout=True, env={'RUNTIME_TYPE_CHECKING_MODE': 'WARNING'}),
    ]


def test_get_pythons(monkeypatch):
    monkeypatch.setattr(_noxfile, 'get_tool_versions', Mock(return_value={'python': ['3.10', '3.12', '3.10']}))
    _get_pythons.cache_clear()
    try:
        assert sorted(_get_pythons()) == ['3.10', '3.12']
    finally:
        _get_pythons.cache_clear()
