"""Test file_helpers."""

from pathlib import Path

from calcipy.file_helpers import delete_dir, ensure_dir, read_lines, sanitize_filename, tail_lines

from .configuration import TEST_TMP_CACHE


def test_sanitize_filename():
    """Test sanitize_filename."""
    result = sanitize_filename('_dash-09-ϑ//.// SUPER.py')

    assert result == '_dash-09-___.___SUPER.py'


def test_read_lines():
    """Test read_lines."""
    result = read_lines(Path(__file__).resolve())

    assert result[0] == '"""Test file_helpers."""'
    assert len(result) > 22


def test_tail_lines():
    """Test tail_lines."""
    path_file = TEST_TMP_CACHE / 'tmp.txt'
    path_file.write_text('line 1\nline 2\n')

    result = tail_lines(path_file, count=1)

    assert result == ['']
    assert tail_lines(path_file, count=2) == ['line 2', '']
    assert tail_lines(path_file, count=10) == ['line 1', 'line 2', '']


def test_dir_tools():
    """Test delete_dir & ensure_dir."""
    tmp_dir = TEST_TMP_CACHE / '.tmp-test_delete_dir'
    tmp_dir.mkdir(exist_ok=True)
    (tmp_dir / 'tmp.txt').write_text('Placeholder\n')
    tmp_subdir = tmp_dir / 'subdir'

    ensure_dir(tmp_subdir)  # act

    assert tmp_subdir.is_dir()
    delete_dir(tmp_dir)
    assert not tmp_dir.is_dir()
