"""Test code_tag_collector.py."""

import re

from calcipy.code_tag_collector import CODE_TAG_RE, _CodeTag, _format_report, _search_lines, _Tags, write_code_tag_file

from .configuration import PATH_TEST_PROJECT


def test_search_lines():
    """Test _search_lines."""
    lines = [
        '',
        '# DEBUG: Show dodo.py in the documentation',  # noqa: T001
        '# FIXME: Show README.md in the documentation (may need to update paths?)',  # noqa: T100
        '# FYI: Replace src_examples_dir and make more generic to specify code to include in documentation',
        '# HACK: Show table of contents in __init__.py file',  # noqa: T103
        '# NOTE: Show table of contents in __init__.py file',
        '# PLANNED: Show table of contents in __init__.py file',
        '# REVIEW: Show table of contents in __init__.py file',
        '# TBD: Show table of contents in __init__.py file',
        '# TODO: Show table of contents in __init__.py file',  # noqa: T101
        'class Code: # TODO: Complete',  # noqa: T101
        '   //TODO: Not matched',  # noqa: T101
        '   pass  # Both FIXME: and TODO: in the same line, but only match the first',  # noqa: T100,T101
    ]
    tag_order = ['FIXME', 'FYI', 'HACK', 'REVIEW']  # noqa: T100
    regex_compiled = re.compile(CODE_TAG_RE.format(tag='|'.join(tag_order)))

    comments = _search_lines(lines, regex_compiled)  # act

    assert len(comments) == 5
    assert comments[0].lineno == 3
    assert comments[0].tag == 'FIXME'  # noqa: T100
    assert comments[0].text == 'Show README.md in the documentation (may need to update paths?)'
    assert comments[-1].tag == 'FIXME'  # noqa: T100
    assert comments[-1].text == 'and TODO: in the same line, but only match the first'  # noqa: T101


def test_format_report():
    """Test _format_report."""
    lines = ['# DEBUG: Example 1', '# TODO: Example 2']  # noqa: T101
    comments = [_CodeTag(lineno, *line.split('# ')[1].split(': ')) for lineno, line in enumerate(lines)]
    tagged_collection = [_Tags(path_source=PATH_TEST_PROJECT, code_tags=comments)]
    tag_order = ['TODO']  # noqa: T101
    # Expected that DEBUG won't be matched
    expected = f"""- {PATH_TEST_PROJECT.name}
    - line   1    TODO: Example 2

Found code tags for TODO (1)
"""  # noqa: T100,T101

    output = _format_report(PATH_TEST_PROJECT.parent, tagged_collection, tag_order=tag_order)  # act

    assert output == expected, f'Received: `{output}`'


def test_write_code_tag_file(fix_test_cache):
    """Test _write_code_tag_file for an empty file."""
    path_tag_summary = fix_test_cache / 'code_tags.md'
    tmp_code_file = fix_test_cache / 'tmp.code'
    tmp_code_file.write_text('')

    write_code_tag_file(
        path_tag_summary=path_tag_summary, paths_source=[tmp_code_file], base_dir=fix_test_cache,
    )  # act

    assert not path_tag_summary.is_file()


# calcipy:skip_tags
