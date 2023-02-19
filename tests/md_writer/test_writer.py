"""Test doit_tasks/doc.py."""

import json
import shutil
from functools import partial
from pathlib import Path

import pytest
from beartype import beartype
from beartype.typing import List

from calcipy.md_writer._writer import (
    _format_cov_table,
    _handle_coverage,
    _handle_source_file,
    _parse_var_comment,
    write_autoformatted_md_sections,
)

from ..configuration import TEST_DATA_DIR

SAMPLE_README_PATH = TEST_DATA_DIR / 'sample_doc_files' / 'README.md'

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
    path_new_readme = fix_test_cache / SAMPLE_README_PATH.name
    shutil.copyfile(SAMPLE_README_PATH, path_new_readme)
    path_cover = fix_test_cache / 'coverage.json'
    path_cover.write_text(json.dumps(_COVERAGE_SAMPLE_DATA))
    placeholder = '<!-- {cts} SOURCE_FILE_TEST=/tests/conftest.py; -->\n<!-- {cte} -->'
    was_placeholder = placeholder in path_new_readme.read_text()

    write_autoformatted_md_sections(handler_lookup={
        'SOURCE_FILE_TEST': _handle_source_file,
        'COVERAGE_TEST': partial(_handle_coverage, path_coverage=path_cover),
    }, paths_md=[path_new_readme])

    text = path_new_readme.read_text()
    assert was_placeholder
    assert placeholder not in text
    assert '<!-- {cts} COVERAGE_TEST -->\n| File    ' in text
    assert '| File                              |   Statements |   Missing |   Excluded | Coverage   |' in text
    assert '| `calcipy/doit_tasks/base.py`      |           22 |         2 |          3 | 90.9%      |' in text
    assert '| **Totals**                        |           97 |        46 |          3 | 52.6%      |' in text
    assert 'Generated on: 2021-06-03' in text
    assert '<!-- {cts} SOURCE_FILE_TEST=/tests/conftest.py; -->\n```py\n"""PyTest configuration.' in text


@pytest.mark.parametrize(
    ('line', 'match'), [
        ('<!-- {cts} rating=1; (User can specify rating on scale of 1-5) -->', {'rating': '1'}),
        ('<!-- {cts} path_image=imgs/image_filename.png; -->', {'path_image': 'imgs/image_filename.png'}),
        ('<!-- {cts} tricky_var_3=-11e-21; -->', {'tricky_var_3': '-11e-21'}),
    ],
)
def test_parse_var_comment(line, match):
    result = _parse_var_comment(line)

    assert result == match


@beartype
def _star_parser(line: str, path_md: Path) -> List[str]:  # noqa: ARG001
    rating = int(_parse_var_comment(line)['rating'])
    return [f'RATING={rating}']


def test_write_autoformatted_md_sections_custom(fix_test_cache):
    path_new_readme = fix_test_cache / SAMPLE_README_PATH.name
    shutil.copyfile(SAMPLE_README_PATH, path_new_readme)

    write_autoformatted_md_sections(handler_lookup={'rating': _star_parser}, paths_md=[path_new_readme])

    text = path_new_readme.read_text()
    assert '\n<!-- {cts} rating=' in SAMPLE_README_PATH.read_text()
    assert '\n<!-- {cts} rating=' not in text
    assert '\n\nRATING=4\n\n' in text
    assert """<!-- {cts} name_image=NA.png; (User can specify image name) -->
<!-- Capture image -->
<!-- {cte} -->""" in text
