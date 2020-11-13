"""Test tag_collector.py."""

from pathlib import Path

from dash_dev.tag_collector import _format_report, _search_lines, _TaggedComment, _TaggedComments

from .configuration import DIG_CWD


def test_search_lines():
    """Test _search_lines."""
    lines = [
        '',
        '# DEBUG: Show dodo.py in the documentation',
        '# FIXME: Show README.md in the documentation (may need to update paths?)',
        '# FYI: Replace src_examples_dir and make more generic to specify code to include in documentation',
        '# HACK: Show table of contents in __init__.py file',
        '# NOTE: Show table of contents in __init__.py file',
        '# PLANNED: Show table of contents in __init__.py file',
        '# REVIEW: Show table of contents in __init__.py file',
        '# TBD: Show table of contents in __init__.py file',
        '# TODO: Show table of contents in __init__.py file',
        'class Code: # TODO: Complete',
        '   //TODO: Not matched',
        '   pass  # Both FIXME: and TODO: in the same line, but only match the first',
    ]

    comments = _search_lines(lines)  # act

    assert len(comments) == 11
    assert comments[1].lineno == 3
    assert comments[1].tag == 'FIXME'
    assert comments[1].text == 'Show README.md in the documentation (may need to update paths?)'
    assert comments[-1].tag == 'FIXME'
    assert comments[-1].text == 'and TODO: in the same line, but only match the first'


def test_format_report():
    """Test _format_report."""
    lines = ['# DEBUG: Example 1', '# TODO: Example 2']
    comments = [_TaggedComment(lineno, *line.split(': ')) for lineno, line in enumerate(lines)]
    tagged_collection = [_TaggedComments(file_path=DIG_CWD, tagged_comments=comments)]

    output = _format_report(Path().resolve(), tagged_collection)  # act

    expected = """tests/data/doit_project
    line   0 # DEBUG: Example 1
    line   1  # TODO: Example 2

Found tagged comments for # DEBUG (1),  # TODO (1)
"""
    assert output == expected, f'`{output}`'
