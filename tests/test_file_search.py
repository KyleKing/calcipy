from calcipy.file_helpers import get_relative
from calcipy.file_search import find_project_files_by_suffix

from .configuration import TEST_DATA_DIR

SAMPLE_README_DIR = TEST_DATA_DIR / 'sample_doc_files'


def test_find_project_files_by_suffix():
    expected_suffixes = ['', 'md']

    result = find_project_files_by_suffix(SAMPLE_README_DIR, ignore_patterns=[])

    assert len(result) != 0
    assert sorted(result.keys()) == expected_suffixes
    assert result[''][0].name == '.dotfile'
    rel_pth = get_relative(result['md'][-1], SAMPLE_README_DIR)
    assert rel_pth
    assert rel_pth.as_posix() == 'README.md'
