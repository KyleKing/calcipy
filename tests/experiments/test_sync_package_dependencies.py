"""Tests for sync_package_dependencies."""


from calcipy.experiments.sync_package_dependencies import (
    _collect_pyproject_versions,
    _extract_base_version,
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
