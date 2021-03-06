"""Test code_tag_collector.py."""

# :skip_tags:

from calcipy.doit_tasks import DIG
from calcipy.doit_tasks.code_tag_collector import _CodeTag, _format_report, _search_lines, _Tags

from ..configuration import PATH_TEST_PROJECT, TEST_DIR


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
    regex_compiled = DIG.ct.compile_issue_regex()

    comments = _search_lines(lines, regex_compiled)  # act

    assert len(comments) == 11
    assert comments[1].lineno == 3
    assert comments[1].tag == 'FIXME'  # noqa: T100
    assert comments[1].text == 'Show README.md in the documentation (may need to update paths?)'
    assert comments[-1].tag == 'FIXME'  # noqa: T100
    assert comments[-1].text == 'and TODO: in the same line, but only match the first'  # noqa: T101


def test_format_report():
    """Test _format_report."""
    lines = ['# DEBUG: Example 1', '# TODO: Example 2']  # noqa: T101
    comments = [_CodeTag(lineno, *line.split('# ')[1].split(': ')) for lineno, line in enumerate(lines)]
    tagged_collection = [_Tags(path_source=PATH_TEST_PROJECT, code_tags=comments)]

    output = _format_report(TEST_DIR, tagged_collection)  # act

    expected = """- data/doit_project
    - line   0   DEBUG: Example 1
    - line   1    TODO: Example 2

Found code tags for TODO (1), DEBUG (1)
"""  # noqa: T100,T101
    assert output == expected, f'Received: `{output}`'
