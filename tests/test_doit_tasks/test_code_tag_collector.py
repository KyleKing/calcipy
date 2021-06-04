"""Test code_tag_collector.py."""

from calcipy.doit_tasks import DG
from calcipy.doit_tasks.code_tag_collector import (
    _CodeTag, _format_report, _search_lines, _Tags, _write_code_tag_file, task_collect_code_tags,
)

from ..configuration import PATH_TEST_PROJECT


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
    regex_compiled = DG.ct.compile_issue_regex()

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

    output = _format_report(PATH_TEST_PROJECT.parent, tagged_collection)  # act

    # FIXME: DEBUG SHOULDN'T have been matched!
    expected = f"""- {PATH_TEST_PROJECT.name}
    - line   0   DEBUG: Example 1
    - line   1    TODO: Example 2

Found code tags for TODO (1)
"""  # noqa: T100,T101
    assert output == expected, f'Received: `{output}`'


def test_write_code_tag_file(fix_test_cache):
    """Test _write_code_tag_file for an empty file."""
    path_tag_summary = fix_test_cache / 'code_tags.md'
    tmp_code_file = fix_test_cache / 'tmp.code'
    tmp_code_file.write_text('')
    #
    paths_original = DG.meta.paths
    DG.meta.paths = [tmp_code_file]

    _write_code_tag_file(path_tag_summary)  # act

    assert not path_tag_summary.is_file()
    #
    DG.meta.paths = paths_original


def test_task_collect_code_tags():
    """Test task_collect_code_tags."""
    result = task_collect_code_tags()

    actions = result['actions']
    assert len(actions) == 1
    assert isinstance(actions[0][0], type(_write_code_tag_file))


# calcipy:skip_tags
