"""Test doit_tasks/doc.py."""

import json
import shutil
from copy import deepcopy
from pathlib import Path

import pytest
from beartype.typing import List

from calcipy.doit_tasks.doc import (
    _format_cov_table, _handle_coverage, _handle_source_file, _is_mkdocs_local,
    _move_cl, _parse_var_comment, task_cl_bump, task_cl_bump_pre, task_cl_write,
    task_deploy_docs, task_document, task_open_docs, write_autoformatted_md_sections,
)
from calcipy.doit_tasks.doit_globals import get_dg

from ..configuration import TEST_DATA_DIR


def test_move_cl():
    """Test _move_cl."""
    path_cl = get_dg().meta.path_project / 'CHANGELOG.md'
    path_cl.write_text('# CHANGELOG')
    path_cl_dest = get_dg().doc.doc_sub_dir / path_cl.name

    _move_cl()  # act

    assert not path_cl.is_file()
    assert path_cl_dest.is_file()
    path_cl_dest.unlink()


def test_task_cl_write(assert_against_cache):
    """Test task_cl_write."""
    result = task_cl_write()

    assert_against_cache(result)


def test_task_cl_bump(assert_against_cache):
    """Test task_cl_bump."""
    result = task_cl_bump()

    assert_against_cache(result)


def test_task_cl_bump_pre(assert_against_cache):
    """Test task_cl_bump_pre."""
    result = task_cl_bump_pre()

    assert_against_cache(result)


_COVERAGE_SAMPLE_DATA = {
    'meta': {'timestamp': '2021-06-03T19:37:11.980123'},
    'files': {
        'calcipy/doit_tasks/base.py': {
            'summary': {
                'covered_lines': 20,
                'num_statements': 22,
                'percent_covered': 90.9090909090909,
                'missing_lines': 2,
                'excluded_lines': 3,
            },
        },
        'calcipy/doit_tasks/code_tags.py': {
            'summary': {
                'covered_lines': 31,
                'num_statements': 75,
                'percent_covered': 41.333333333333336,
                'missing_lines': 44,
                'excluded_lines': 0,
            },
        },
    },
    'totals': {
        'covered_lines': 51,
        'num_statements': 97,
        'percent_covered': 52.57732,
        'missing_lines': 46,
        'excluded_lines': 3,
    },
}
"""Sample coverage data generated with `python -m coverage json`."""


def test_format_cov_table():
    """Test _format_cov_table."""
    result = _format_cov_table(_COVERAGE_SAMPLE_DATA)

    assert result == [
        '| File                              |   Statements |   Missing |   Excluded | Coverage   |',
        '|-----------------------------------|--------------|-----------|------------|------------|',
        '| `calcipy/doit_tasks/base.py`      |           22 |         2 |          3 | 90.9%      |',
        '| `calcipy/doit_tasks/code_tags.py` |           75 |        44 |          0 | 41.3%      |',
        '| **Totals**                        |           97 |        46 |          3 | 52.6%      |',
        '',
        'Generated on: 2021-06-03',
    ]


def test_write_autoformatted_md_sections(fix_test_cache):
    """Test write_autoformatted_md_sections."""
    path_md_file = TEST_DATA_DIR / 'sample_doc_files' / 'README.md'
    path_new_readme = fix_test_cache / path_md_file.name
    shutil.copyfile(path_md_file, path_new_readme)
    (get_dg().meta.path_project / 'coverage.json').write_text(json.dumps(_COVERAGE_SAMPLE_DATA))
    #
    paths_original = get_dg().doc.paths_md
    lookup_original = deepcopy(get_dg().doc.handler_lookup)
    #
    get_dg().doc.paths_md = [path_new_readme]
    get_dg().doc.handler_lookup = {
        'SOURCE_FILE_TEST': _handle_source_file,
        'COVERAGE_TEST': _handle_coverage,
    }

    write_autoformatted_md_sections()  # act

    text = path_new_readme.read_text()
    assert '<!-- {cts} SOURCE_FILE_TEST=/tests/conftest.py; -->\n<!-- {cte} -->' not in text
    assert '<!-- {cts} SOURCE_FILE_TEST=/tests/conftest.py; -->\n```py\n"""PyTest configuration."""\n' in text
    assert '<!-- {cts} COVERAGE_TEST -->\n| File                  ' in text
    #
    get_dg().doc.paths_md = paths_original
    get_dg().doc.handler_lookup = lookup_original


@pytest.mark.parametrize(
    ('line', 'match'), [
        ('<!-- {cts} rating=1; (User can specify rating on scale of 1-5) -->', {'rating': '1'}),
        ('<!-- {cts} path_image=imgs/image_filename.png; -->', {'path_image': 'imgs/image_filename.png'}),
        ('<!-- {cts} tricky_var_3=-11e-21; -->', {'tricky_var_3': '-11e-21'}),
    ],
)
def test_parse_var_comment(line, match):
    """Test _parse_var_comment."""
    result = _parse_var_comment(line)

    assert result == match


def _star_parser(line: str, path_md: Path) -> List[str]:
    rating = int(_parse_var_comment(line)['rating'])
    return [f'RATING={rating}']


def test_write_autoformatted_md_sections_custom(fix_test_cache):
    """Test write_autoformatted_md_sections with custom handlers."""
    path_md_file = TEST_DATA_DIR / 'sample_doc_files' / 'README.md'
    path_new_readme = fix_test_cache / path_md_file.name
    shutil.copyfile(path_md_file, path_new_readme)
    #
    paths_original = get_dg().doc.paths_md
    lookup_original = deepcopy(get_dg().doc.handler_lookup)
    #
    get_dg().doc.paths_md = [path_new_readme]
    get_dg().doc.handler_lookup = {
        'rating': _star_parser,
    }

    write_autoformatted_md_sections()  # act

    text = path_new_readme.read_text()
    assert '\n<!-- {cts} rating=' in path_md_file.read_text()
    assert '\n<!-- {cts} rating=' not in text
    assert '\n\nRATING=4\n\n' in text
    assert """<!-- {cts} name_image=NA.png; (User can specify image name) -->
<!-- Capture image -->
<!-- {cte} -->""" in text
    #
    get_dg().doc.paths_md = paths_original
    get_dg().doc.handler_lookup = lookup_original


def test_task_document(assert_against_cache):
    """Test task_document."""
    result = task_document()

    assert _is_mkdocs_local() is False
    assert_against_cache(result)


def test_task_open_docs(assert_against_cache):
    """Test task_open_docs."""
    result = task_open_docs()

    assert _is_mkdocs_local() is False
    assert_against_cache(result)


def test_task_deploy_docs(assert_against_cache):
    """Test task_deploy_docs."""
    result = task_deploy_docs()

    assert_against_cache(result)
