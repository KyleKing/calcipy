"""Tests for sync_package_dependencies."""

from pathlib import Path
from textwrap import dedent

from calcipy.experiments.sync_package_dependencies import (
    _collect_pyproject_versions,
    _extract_base_version,
    _parse_lock_file,
    _replace_pyproject_versions,
)


def test_extract_base_version():
    """Test _extract_base_version function."""
    assert _extract_base_version('>=1.0.0,<2.0.0') == '1.0.0'
    assert _extract_base_version('1.0.0') == '1.0.0'
    assert _extract_base_version('^1.0.0') == '1.0.0'


def test_collect_pyproject_versions():
    """Test _collect_pyproject_versions function."""
    pyproject_text = """
[tool.poetry.dependencies]
python = "^3.9"
requests = ">=2.0.0,<3.0.0"
flask = "2.0.0"
"""
    versions = _collect_pyproject_versions(pyproject_text)
    assert versions == {'requests': '2.0.0', 'flask': '2.0.0'}


def test_replace_pyproject_versions():
    """Test _replace_pyproject_versions function."""
    pyproject_text = """
[tool.poetry.dependencies]
requests = ">=2.0.0,<3.0.0"
flask = "2.0.0"
"""
    lock_versions = {'requests': '2.1.0', 'flask': '2.1.0'}
    pyproject_versions = {'requests': '2.0.0', 'flask': '2.0.0'}
    new_text = _replace_pyproject_versions(lock_versions, pyproject_versions, pyproject_text)
    assert '>=2.1.0,<3.0.0' in new_text
    assert 'flask = "2.1.0"' in new_text


def test_collect_pyproject_versions_uv_format():
    """Test _collect_pyproject_versions with UV format."""
    pyproject_text = dedent("""
        [project]
        dependencies = [
            "requests>=2.0.0",
            "flask>=2.0.0",
        ]

        [project.optional-dependencies]
        dev = [
            "pytest>=7.0.0",
        ]

        [dependency-groups]
        docs = [
            "mkdocs>=1.5.0",
        ]
    """)
    versions = _collect_pyproject_versions(pyproject_text)
    assert versions == {
        'requests': '2.0.0',
        'flask': '2.0.0',
        'pytest': '7.0.0',
        'mkdocs': '1.5.0',
    }


def test_collect_pyproject_versions_mixed_format():
    """Test _collect_pyproject_versions with both poetry and uv formats."""
    pyproject_text = dedent("""
        [project]
        dependencies = [
            "requests>=2.0.0",
        ]

        [tool.poetry.dependencies]
        flask = "2.0.0"
    """)
    versions = _collect_pyproject_versions(pyproject_text)
    assert 'requests' in versions
    assert 'flask' in versions
    assert versions['requests'] == '2.0.0'
    assert versions['flask'] == '2.0.0'


def test_parse_lock_file_uv(tmp_path: Path):
    """Test _parse_lock_file with uv.lock format."""
    uv_lock = tmp_path / 'uv.lock'
    uv_lock.write_text(dedent("""
        version = 1

        [[package]]
        name = "requests"
        version = "2.31.0"

        [[package]]
        name = "flask"
        version = "3.0.0"
    """))

    versions = _parse_lock_file(uv_lock)
    assert versions == {'requests': '2.31.0', 'flask': '3.0.0'}


def test_parse_lock_file_poetry(tmp_path: Path):
    """Test _parse_lock_file with poetry.lock format."""
    poetry_lock = tmp_path / 'poetry.lock'
    poetry_lock.write_text(dedent("""
        [[package]]
        name = "requests"
        version = "2.31.0"

        [[package]]
        name = "flask"
        version = "3.0.0"
    """))

    versions = _parse_lock_file(poetry_lock)
    assert versions == {'requests': '2.31.0', 'flask': '3.0.0'}
