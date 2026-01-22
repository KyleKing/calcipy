import re

import pytest

from calcipy.code_tag_collector import write_code_tag_file
from calcipy.code_tag_collector._collector import (
    CODE_TAG_RE,
    _CodeTag,
    _format_report,
    _search_lines,
    _Tags,
    github_blame_url,
)
from tests.configuration import TEST_DATA_DIR

TEST_PROJECT = TEST_DATA_DIR / 'test_project'


@pytest.mark.parametrize(
    ('clone_uri', 'expected'),
    [
        ('https://github.com/KyleKing/calcipy.git', 'https://github.com/KyleKing/calcipy'),
        ('git@github.com:KyleKing/calcipy.git', 'https://github.com/KyleKing/calcipy'),
        ('unknown/repo.svn', ''),
        ('', ''),
    ],
)
def test_github_blame_url(clone_uri: str, expected: str):
    assert github_blame_url(clone_uri) == expected


def test__search_lines(snapshot):
    lines = [
        '# DEBUG: Show dodo.py in the documentation',
        'print("FIXME: Show README.md in the documentation (may need to update paths?)")',
        '# FYI: Replace src_examples_dir and make more generic to specify code to include in documentation',
        '# HACK: Show table of contents in __init__.py file',
        '# NOTE: Show table of contents in __init__.py file',
        '# PLANNED: Show table of contents in __init__.py file',
        '# REVIEW: Show table of contents in __init__.py file',
        '# TBD: Show table of contents in __init__.py file',
        '# TODO: Show table of contents in __init__.py file',
        '# HACK - Support unconventional dashed code tags',
        'class Code: # TODO: Complete',
        '   //TODO: Not matched',
        '   ...  # Both FIXME: and FYI: in the same line, but only match the first',
        '# FIXME: ' + 'For a long line is ignored ...' * 14,
    ]
    tag_order = ['FIXME', 'FYI', 'HACK', 'REVIEW']
    matcher = CODE_TAG_RE.format(tag='|'.join(tag_order))

    comments = _search_lines(lines, re.compile(matcher))

    assert comments == snapshot


def test__format_report(fake_process, snapshot):
    fake_process.pass_command([fake_process.any()])  # Allow "git blame" and other commands to run unregistered
    fake_process.keep_last_process(keep=True)
    lines = ['# DEBUG: Example 1', '# TODO: Example 2']
    comments = [
        _CodeTag(lineno=lineno, **dict(zip(('tag', 'text'), line.split('# ')[1].split(': '), strict=False)))
        for lineno, line in enumerate(lines)
    ]
    tagged_collection = [_Tags(path_source=TEST_DATA_DIR / 'test_project', code_tags=comments)]
    tag_order = ['TODO']

    output = _format_report(TEST_DATA_DIR.parent, tagged_collection, tag_order=tag_order)

    assert output == snapshot


def test_write_code_tag_file_when_no_matches(fix_test_cache):
    path_tag_summary = fix_test_cache / 'code_tags.md'
    path_tag_summary.write_text('Should be removed.')
    tmp_code_file = fix_test_cache / 'tmp.code'
    tmp_code_file.write_text('No FIXMES or TODOS here')

    write_code_tag_file(
        path_tag_summary=path_tag_summary, paths_source=[tmp_code_file], base_dir=fix_test_cache,
    )

    assert not path_tag_summary.is_file()


# calcipy_skip_tags
