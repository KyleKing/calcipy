"""Tests for calcipy._corallium.file_helpers module."""


import pytest

from calcipy._corallium.file_helpers import _parse_mise_lock, _parse_mise_toml, get_tool_versions


def test__parse_mise_toml_with_tools_array(tmp_path):
    """Test parsing mise.toml with array of Python versions in [tools] section."""
    mise_toml = tmp_path / 'mise.toml'
    mise_toml.write_text("""
[tools]
python = ["3.12.5", "3.9.13"]
node = ["20.0.0"]
""")

    result = _parse_mise_toml(mise_toml)

    assert result == {
        'python': ['3.12.5', '3.9.13'],
        'node': ['20.0.0'],
    }


def test__parse_mise_toml_with_tools_string(tmp_path):
    """Test parsing mise.toml with single string Python version in [tools] section."""
    mise_toml = tmp_path / 'mise.toml'
    mise_toml.write_text("""
[tools]
python = "3.11.0"
""")

    result = _parse_mise_toml(mise_toml)

    assert result == {'python': ['3.11.0']}


def test__parse_mise_lock_with_single_tool(tmp_path):
    """Test parsing mise.lock with single Python version."""
    mise_lock = tmp_path / 'mise.lock'
    mise_lock.write_text("""
[tools.python]
version = "3.12.5"
backend = "core:python"
""")

    result = _parse_mise_lock(mise_lock)

    assert result == {'python': ['3.12.5']}


def test__parse_mise_lock_with_multiple_tools(tmp_path):
    """Test parsing mise.lock with multiple tools."""
    mise_lock = tmp_path / 'mise.lock'
    mise_lock.write_text("""
[tools.python]
version = "3.11.0"
backend = "core:python"

[tools.node]
version = "20.0.0"
backend = "core:node"
""")

    result = _parse_mise_lock(mise_lock)

    assert result == {
        'python': ['3.11.0'],
        'node': ['20.0.0'],
    }


def test__parse_mise_lock_empty(tmp_path):
    """Test parsing empty mise.lock file."""
    mise_lock = tmp_path / 'mise.lock'
    mise_lock.write_text('')

    result = _parse_mise_lock(mise_lock)

    assert result == {}


def test__parse_mise_toml_empty(tmp_path):
    """Test parsing empty mise.toml file."""
    mise_toml = tmp_path / 'mise.toml'
    mise_toml.write_text('')

    result = _parse_mise_toml(mise_toml)

    assert result == {}


def test_get_tool_versions_with_mise_toml(tmp_path, monkeypatch):
    """Test get_tool_versions reads mise.toml when present."""
    mise_toml = tmp_path / 'mise.toml'
    mise_toml.write_text("""
[tools]
python = ["3.12.5", "3.9.13"]
""")

    monkeypatch.chdir(tmp_path)

    result = get_tool_versions(cwd=tmp_path)

    assert result == {'python': ['3.12.5', '3.9.13']}


def test_get_tool_versions_with_tool_versions(tmp_path, monkeypatch):
    """Test get_tool_versions falls back to .tool-versions when mise.toml doesn't exist."""
    tool_versions = tmp_path / '.tool-versions'
    tool_versions.write_text('python 3.11.0 3.10.0\nnode 18.0.0\n')

    monkeypatch.chdir(tmp_path)

    result = get_tool_versions(cwd=tmp_path)

    assert result == {
        'python': ['3.11.0', '3.10.0'],
        'node': ['18.0.0'],
    }


def test_get_tool_versions_prefers_mise_lock(tmp_path, monkeypatch):
    """Test get_tool_versions prefers mise.lock over mise.toml and .tool-versions."""
    # Create all three files
    mise_lock = tmp_path / 'mise.lock'
    mise_lock.write_text("""
[tools.python]
version = "3.13.0"
backend = "core:python"
""")

    mise_toml = tmp_path / 'mise.toml'
    mise_toml.write_text("""
[tools]
python = ["3.12.5"]
""")

    tool_versions = tmp_path / '.tool-versions'
    tool_versions.write_text('python 3.11.0\n')

    monkeypatch.chdir(tmp_path)

    result = get_tool_versions(cwd=tmp_path)

    # Should use mise.lock (highest priority)
    assert result == {'python': ['3.13.0']}


def test_get_tool_versions_prefers_mise_toml_over_tool_versions(tmp_path, monkeypatch):
    """Test get_tool_versions prefers mise.toml over .tool-versions when no mise.lock exists."""
    mise_toml = tmp_path / 'mise.toml'
    mise_toml.write_text("""
[tools]
python = ["3.12.5"]
""")

    tool_versions = tmp_path / '.tool-versions'
    tool_versions.write_text('python 3.11.0\n')

    monkeypatch.chdir(tmp_path)

    result = get_tool_versions(cwd=tmp_path)

    # Should use mise.toml, not .tool-versions
    assert result == {'python': ['3.12.5']}


def test_get_tool_versions_file_not_found(tmp_path, monkeypatch):
    """Test get_tool_versions raises error when neither file exists."""
    monkeypatch.chdir(tmp_path)

    with pytest.raises(FileNotFoundError):
        get_tool_versions(cwd=tmp_path)
