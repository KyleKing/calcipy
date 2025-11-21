"""Tests for sync_package_dependencies."""

from pathlib import Path
from textwrap import dedent

from calcipy.experiments.sync_package_dependencies import (
    _collect_pyproject_versions,
    _collect_poetry_dependencies,
    _collect_uv_dependencies,
    _extract_base_version,
    _parse_lock_file,
    _parse_pep621_dependency,
    _replace_pyproject_versions,
)


def test_extract_base_version():
    """Test _extract_base_version function."""
    assert _extract_base_version('>=1.0.0,<2.0.0') == '1.0.0'
    assert _extract_base_version('1.0.0') == '1.0.0'
    assert _extract_base_version('^1.0.0') == '1.0.0'
    assert _extract_base_version('~=1.2.3') == '1.2.3'


def test_parse_pep621_dependency():
    """Test _parse_pep621_dependency function."""
    # Simple package
    assert _parse_pep621_dependency('requests>=2.0.0') == ('requests', '2.0.0')
    assert _parse_pep621_dependency('flask==3.0.0') == ('flask', '3.0.0')

    # Package with single extra
    assert _parse_pep621_dependency('mkdocstrings[python]>=0.26.1') == ('mkdocstrings', '0.26.1')

    # Package with multiple extras
    assert _parse_pep621_dependency('package[extra1,extra2]>=1.0.0') == ('package', '1.0.0')

    # Package without version
    assert _parse_pep621_dependency('package') is None
    assert _parse_pep621_dependency('package[extra]') is None

    # Complex version specifiers
    assert _parse_pep621_dependency('package>=1.0.0,<2.0.0') == ('package', '1.0.0')


def test_collect_pyproject_versions_poetry():
    """Test _collect_pyproject_versions with Poetry format."""
    pyproject_text = """
[tool.poetry.dependencies]
python = "^3.9"
requests = ">=2.0.0,<3.0.0"
flask = "2.0.0"
"""
    versions = _collect_pyproject_versions(pyproject_text)
    assert versions == {'requests': '2.0.0', 'flask': '2.0.0'}


def test_replace_pyproject_versions_poetry():
    """Test _replace_pyproject_versions with Poetry format."""
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


def test_collect_uv_dependencies():
    """Test _collect_uv_dependencies function."""
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
    from corallium.tomllib import tomllib

    pyproject = tomllib.loads(pyproject_text)
    versions = _collect_uv_dependencies(pyproject)
    assert versions == {
        'requests': '2.0.0',
        'flask': '2.0.0',
        'pytest': '7.0.0',
        'mkdocs': '1.5.0',
    }


def test_collect_uv_dependencies_with_extras():
    """Test _collect_uv_dependencies handles packages with extras."""
    pyproject_text = dedent("""
        [project]
        dependencies = [
            "mkdocstrings[python]>=0.26.1",
            "hypothesis[cli]>=6.112.4",
        ]
    """)
    from corallium.tomllib import tomllib

    pyproject = tomllib.loads(pyproject_text)
    versions = _collect_uv_dependencies(pyproject)
    assert versions == {
        'mkdocstrings': '0.26.1',
        'hypothesis': '6.112.4',
    }


def test_collect_poetry_dependencies():
    """Test _collect_poetry_dependencies function."""
    pyproject_text = dedent("""
        [tool.poetry.dependencies]
        requests = ">=2.0.0"
        flask = "2.0.0"

        [tool.poetry.group.dev.dependencies]
        pytest = "^7.0.0"
    """)
    from corallium.tomllib import tomllib

    pyproject = tomllib.loads(pyproject_text)
    versions = _collect_poetry_dependencies(pyproject)
    assert 'requests' in versions
    assert 'flask' in versions
    assert 'pytest' in versions


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


def test_replace_pyproject_versions_pep621_format():
    """Test _replace_pyproject_versions with PEP 621 list format."""
    pyproject_text = dedent("""
        [project]
        dependencies = [
            "requests>=2.0.0",
            "flask>=2.0.0",
        ]
    """)
    lock_versions = {'requests': '2.1.0', 'flask': '2.1.0'}
    pyproject_versions = {'requests': '2.0.0', 'flask': '2.0.0'}
    new_text = _replace_pyproject_versions(lock_versions, pyproject_versions, pyproject_text)

    # Check that versions were updated
    assert 'requests>=2.1.0' in new_text
    assert 'flask>=2.1.0' in new_text
    # Ensure old versions are gone
    assert 'requests>=2.0.0' not in new_text
    assert 'flask>=2.0.0' not in new_text


def test_replace_pyproject_versions_pep621_with_extras():
    """Test _replace_pyproject_versions with packages that have extras."""
    pyproject_text = dedent("""
        [project.optional-dependencies]
        doc = [
            "mkdocstrings[python]>=0.26.1",
        ]
    """)
    lock_versions = {'mkdocstrings': '0.27.0'}
    pyproject_versions = {'mkdocstrings': '0.26.1'}
    new_text = _replace_pyproject_versions(lock_versions, pyproject_versions, pyproject_text)

    # Check that version was updated while preserving extras
    assert 'mkdocstrings[python]>=0.27.0' in new_text
    assert 'mkdocstrings[python]>=0.26.1' not in new_text


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


def test_end_to_end_uv_replacement(tmp_path: Path):
    """Test end-to-end version replacement for UV format."""
    # Create uv.lock
    uv_lock = tmp_path / 'uv.lock'
    uv_lock.write_text(dedent("""
        version = 1

        [[package]]
        name = "requests"
        version = "2.31.0"

        [[package]]
        name = "mkdocstrings"
        version = "0.27.0"
    """))

    # Create pyproject.toml
    pyproject = tmp_path / 'pyproject.toml'
    pyproject.write_text(dedent("""
        [project]
        name = "test-package"
        dependencies = [
            "requests>=2.28.0",
        ]

        [project.optional-dependencies]
        doc = [
            "mkdocstrings[python]>=0.26.0",
        ]
    """))

    # Run replacement
    from calcipy.experiments.sync_package_dependencies import replace_versions

    replace_versions(uv_lock)

    # Verify results
    result = pyproject.read_text()
    assert 'requests>=2.31.0' in result
    assert 'mkdocstrings[python]>=0.27.0' in result
    # Ensure old versions are gone
    assert 'requests>=2.28.0' not in result
    assert 'mkdocstrings[python]>=0.26.0' not in result
