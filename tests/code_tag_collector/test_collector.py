import re

from calcipy.code_tag_collector import write_code_tag_file
from calcipy.code_tag_collector._collector import CODE_TAG_RE, _CodeTag, _format_report, _search_lines, _Tags

from ..configuration import TEST_DATA_DIR

TEST_PROJECT = TEST_DATA_DIR / 'test_project'


def test__search_lines():
    lines = [
        '# DEBUG: Show dodo.py in the documentation',  # noqa: T001
        'print("FIXME: Show README.md in the documentation (may need to update paths?)")',  # noqa: T100
        '# FYI: Replace src_examples_dir and make more generic to specify code to include in documentation',
        '# HACK: Show table of contents in __init__.py file',  # noqa: T103
        '# NOTE: Show table of contents in __init__.py file',
        '# PLANNED: Show table of contents in __init__.py file',
        '# REVIEW: Show table of contents in __init__.py file',
        '# TBD: Show table of contents in __init__.py file',
        '# TODO: Show table of contents in __init__.py file',  # noqa: T101
        '# HACK - Support unconventional dashed code tags',  # noqa: T101
        'class Code: # TODO: Complete',  # noqa: T101
        '   //TODO: Not matched',  # noqa: T101
        '   ...  # Both FIXME: and FYI: in the same line, but only match the first',  # noqa: T100,T101
        '# FIXME: ' + 'For a long line is ignored ...' * 14,  # noqa: T100,T101
    ]
    tag_order = ['FIXME', 'FYI', 'HACK', 'REVIEW']  # noqa: T100
    regex_compiled = re.compile(CODE_TAG_RE.format(tag='|'.join(tag_order)))

    comments = _search_lines(lines, regex_compiled)

    # TODO: assert_against_cache(comments)
    assert [_c.dict() for _c in comments] == [
        {
            'lineno': 2,
            'tag': 'FIXME',
            'text': 'Show README.md in the documentation (may need to update paths?)\")',
        },
        {
            'lineno': 3,
            'tag': 'FYI',
            'text': 'Replace src_examples_dir and make more generic to specify code to include in documentation',
        },
        {
            'lineno': 4,
            'tag': 'HACK',
            'text': 'Show table of contents in __init__.py file',
        },
        {
            'lineno': 7,
            'tag': 'REVIEW',
            'text': 'Show table of contents in __init__.py file',
        },
        {
            'lineno': 10,
            'tag': 'HACK',
            'text': 'Support unconventional dashed code tags',
        },
        {
            'lineno': 13,
            'tag': 'FIXME',
            'text': 'and FYI: in the same line, but only match the first',
        },
    ]


def test__format_report(fake_process):
    fake_process.pass_command([fake_process.any()])  # Allow "git blame" and other commands to run unregistered
    fake_process.keep_last_process(keep=True)
    lines = ['# DEBUG: Example 1', '# TODO: Example 2']  # noqa: T101
    comments = [
        _CodeTag(lineno=lineno, **dict(zip(('tag', 'text'), line.split('# ')[1].split(': '))))  # noqa: B905
        for lineno, line in enumerate(lines)
    ]
    tagged_collection = [_Tags(path_source=TEST_DATA_DIR / 'test_project', code_tags=comments)]
    tag_order = ['TODO']  # noqa: T101

    output = _format_report(TEST_DATA_DIR.parent, tagged_collection, tag_order=tag_order)

    # TODO: assert_against_cache({'output': output.split('\n')})
    assert output.split('\n') == [
        '',
        '| Type   | Comment   | Last Edit   | Source File         |',
        '|--------|-----------|-------------|---------------------|',
        '| TODO   | Example 2 | N/A         | data/test_project:1 |',
        '',
        'Found code tags for TODO (1)',
        '',
    ]


def test_write_code_tag_file_when_no_matches(fix_test_cache):
    path_tag_summary = fix_test_cache / 'code_tags.md'
    tmp_code_file = fix_test_cache / 'tmp.code'
    tmp_code_file.write_text('No FIXMES or TODOS here')

    write_code_tag_file(
        path_tag_summary=path_tag_summary, paths_source=[tmp_code_file], base_dir=fix_test_cache,
    )

    assert not path_tag_summary.is_file()


# calcipy_skip_tags
