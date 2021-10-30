"""Test doit_tasks/doc.py."""

import json
import shutil
import webbrowser
from copy import deepcopy
from pathlib import Path
from typing import List

import pytest

from calcipy.doit_tasks.base import write_text
from calcipy.doit_tasks.doc import (
    _format_cov_table, _handle_coverage, _handle_source_file, _is_mkdocs_local,
    _move_cl, _parse_var_comment, task_cl_bump, task_cl_bump_pre, task_cl_write,
    task_deploy_docs, task_document, task_open_docs, write_autoformatted_md_sections,
)
from calcipy.doit_tasks.doit_globals import DG

from ..configuration import TEST_DATA_DIR


def test_move_cl():
    """Test _move_cl."""
    path_cl = DG.meta.path_project / 'CHANGELOG.md'
    path_cl.write_text('# CHANGELOG')
    path_cl_dest = DG.doc.doc_sub_dir / path_cl.name

    _move_cl()  # act

    assert not path_cl.is_file()
    assert path_cl_dest.is_file()
    path_cl_dest.unlink()


def test_task_cl_write():
    """Test task_cl_write."""
    result = task_cl_write()

    actions = result['actions']
    assert len(actions) == 2
    assert actions[0] == 'poetry run cz changelog'
    assert isinstance(actions[1][0], type(_move_cl))


def test_task_cl_bump():
    """Test task_cl_bump."""
    result = task_cl_bump()

    actions = result['actions']
    assert len(actions) == 4
    assert isinstance(actions[1][0], type(_move_cl))
    assert 'poetry run cz bump --annotated-tag' in str(actions[2])
    assert actions[3] == 'git push origin --tags --no-verify'


def test_task_cl_bump_pre():
    """Test task_cl_bump_pre."""
    result = task_cl_bump_pre()

    actions = result['actions']
    assert len(actions) == 4
    assert isinstance(actions[1][0], type(_move_cl))
    assert 'poetry run cz bump --prerelease' in str(actions[2])
    assert actions[3] == 'git push origin --tags --no-verify'
    params = result['params']
    assert len(params) == 1
    assert params[0]['name'] == 'prerelease'
    assert params[0]['short'] == 'p'


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
        '|:----------------------------------|-------------:|----------:|-----------:|:-----------|',
        '| `calcipy/doit_tasks/base.py`      |           22 |         2 |          3 | 90.9%      |',
        '| `calcipy/doit_tasks/code_tags.py` |           75 |        44 |          0 | 41.3%      |',
        '| **Totals**                        |           97 |        46 |          3 | 52.6%      |',
        '',
        'Generated on: 2021-06-03T19:37:11.980123',
    ]


def test_write_autoformatted_md_sections(fix_test_cache):
    """Test write_autoformatted_md_sections."""
    path_md_file = TEST_DATA_DIR / 'sample_doc_files' / 'README.md'
    path_new_readme = fix_test_cache / path_md_file.name
    shutil.copyfile(path_md_file, path_new_readme)
    (DG.meta.path_project / 'coverage.json').write_text(json.dumps(_COVERAGE_SAMPLE_DATA))
    #
    paths_original = DG.doc.paths_md
    lookup_original = deepcopy(DG.doc.handler_lookup)
    #
    DG.doc.paths_md = [path_new_readme]
    DG.doc.handler_lookup = {
        'SOURCE_FILE_TEST': _handle_source_file,
        'COVERAGE_TEST': _handle_coverage,
    }

    write_autoformatted_md_sections()  # act

    text = path_new_readme.read_text()
    assert '<!-- {cts} SOURCE_FILE_TEST=/tests/conftest.py; -->\n<!-- {cte} -->' not in text
    assert '<!-- {cts} SOURCE_FILE_TEST=/tests/conftest.py; -->\n```py\n"""PyTest configuration."""\n' in text
    assert '<!-- {cts} COVERAGE_TEST -->\n| File                  ' in text
    #
    DG.doc.paths_md = paths_original
    DG.doc.handler_lookup = lookup_original


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
    paths_original = DG.doc.paths_md
    lookup_original = deepcopy(DG.doc.handler_lookup)
    #
    DG.doc.paths_md = [path_new_readme]
    DG.doc.handler_lookup = {
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
    DG.doc.paths_md = paths_original
    DG.doc.handler_lookup = lookup_original


def test_task_document():
    """Test task_document."""
    result = task_document()

    assert _is_mkdocs_local() is False
    actions = result['actions']
    assert len(actions) == 6
    assert isinstance(actions[0][0], type(write_autoformatted_md_sections))
    assert str(actions[2]).startswith('Cmd: poetry run pdocs as_markdown')
    assert isinstance(actions[3][0], type(write_text))
    assert ' pyreverse ' in str(actions[4])
    assert str(actions[-1]).startswith('Cmd: poetry run mkdocs build --site-dir')


def test_task_open_docs():
    """Test task_open_docs."""
    result = task_open_docs()

    assert _is_mkdocs_local() is False
    actions = result['actions']
    assert len(actions) == 2
    assert isinstance(actions[0][0], type(webbrowser.open))
    assert len(actions[0][1]) == 1
    assert actions[0][1][0].startswith('http://localhost')
    assert str(actions[1]).endswith('mkdocs serve --dirtyreload')


def test_task_deploy_docs():
    """Test task_deploy_docs."""
    result = task_deploy_docs()

    actions = result['actions']
    assert len(actions) == 1
    assert str(actions[0]).endswith('mkdocs gh-deploy')
