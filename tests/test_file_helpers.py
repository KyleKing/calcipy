"""Test file_helpers."""

from pathlib import Path

from calcipy.file_helpers import delete_dir, ensure_dir, if_found_unlink, read_lines, sanitize_filename, tail_lines


def test_sanitize_filename():
    result = sanitize_filename('_dash-09-ϑ//.// SUPER.py')

    assert result == '_dash-09-___.___SUPER.py'


def test_read_lines():
    at_least_this_many_lines = 22
    result = read_lines(Path(__file__).resolve())

    assert result[0] == '"""Test file_helpers."""'
    assert len(result) > at_least_this_many_lines
    assert len(read_lines(Path.cwd() / 'not a file.tbd')) == 0


def test_tail_lines(fix_test_cache):
    path_file = fix_test_cache / 'tmp.txt'
    path_file.write_text('line 1\nline 2\n')

    result = tail_lines(path_file, count=1)

    assert result == ['']
    assert tail_lines(path_file, count=2) == ['line 2', '']
    assert tail_lines(path_file, count=10) == ['line 1', 'line 2', '']


def test_if_found_unlink(fix_test_cache):
    path_file = fix_test_cache / 'if_found_unlink-test_file.txt'

    path_file.write_text('')

    assert path_file.is_file()
    if_found_unlink(path_file)
    assert not path_file.is_file()


def test_dir_tools(fix_test_cache):
    tmp_dir = fix_test_cache / '.tmp-test_delete_dir'
    tmp_dir.mkdir(exist_ok=True)
    (tmp_dir / 'tmp.txt').write_text('Placeholder\n')
    tmp_subdir = tmp_dir / 'subdir'

    ensure_dir(tmp_subdir)

    assert tmp_subdir.is_dir()
    delete_dir(tmp_dir)
    assert not tmp_dir.is_dir()
