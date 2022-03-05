"""Test code_tag_collector.py."""

import re

import attrs

from calcipy.code_tag_collector import CODE_TAG_RE, _CodeTag, _format_report, _search_lines, _Tags, write_code_tag_file

from .configuration import PATH_TEST_PROJECT


def test_search_lines(assert_against_cache, benchmark):
    """Test _search_lines."""
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

    comments = benchmark(_search_lines, lines, regex_compiled)  # act

    assert comments[0].lineno == 2
    assert comments[0].tag == 'FIXME'  # noqa: T100
    assert comments[0].text == 'Show README.md in the documentation (may need to update paths?)")'
    assert_against_cache([*map(attrs.asdict, comments)])


def test_format_report(assert_against_cache, benchmark, fake_process):
    """Test _format_report."""
    fake_process.pass_command([fake_process.any()])  # Allow "git blame" and other commands to run unregistered
    fake_process.keep_last_process(True)
    lines = ['# DEBUG: Example 1', '# TODO: Example 2']  # noqa: T101
    comments = [_CodeTag(lineno, *line.split('# ')[1].split(': ')) for lineno, line in enumerate(lines)]
    tagged_collection = [_Tags(path_source=PATH_TEST_PROJECT, code_tags=comments)]
    tag_order = ['TODO']  # noqa: T101

    output = benchmark(_format_report, PATH_TEST_PROJECT.parent, tagged_collection, tag_order=tag_order)  # act

    assert_against_cache({'output': output.split('\n')})


def test_write_code_tag_file_when_no_matches(fix_test_cache, benchmark):
    """Test _write_code_tag_file for an empty file."""
    path_tag_summary = fix_test_cache / 'code_tags.md'
    tmp_code_file = fix_test_cache / 'tmp.code'
    tmp_code_file.write_text('No FIXMES or TODOS here')

    benchmark(
        write_code_tag_file,
        path_tag_summary=path_tag_summary, paths_source=[tmp_code_file], base_dir=fix_test_cache,
    )  # act

    assert not path_tag_summary.is_file()


# calcipy:skip_tags
