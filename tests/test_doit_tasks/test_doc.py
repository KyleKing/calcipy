"""Test doit_tasks/doc.py."""

import shutil
import webbrowser
from pathlib import Path

import pytest

from calcipy.doit_tasks.doc import (
    _move_cl, _parse_var_comment, task_cl_bump, task_cl_bump_pre, task_cl_write,
    task_deploy, task_open_docs, task_serve_docs, write_autoformatted_md_sections,
)
from calcipy.doit_tasks.doit_globals import DG

from ..configuration import TEST_DATA_DIR


def test_move_cl():
    """Test _move_cl."""
    path_cl = DG.meta.path_project / 'CHANGELOG.md'
    path_cl.write_text('# CHANGELOG')
    path_cl_dest = DG.doc.doc_dir / path_cl.name

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
    assert len(actions) == 3
    assert 'poetry run cz bump --changelog --annotated-tag' in str(actions[0])
    assert isinstance(actions[1][0], type(_move_cl))
    assert actions[2] == 'git push origin --tags --no-verify'


def test_task_cl_bump_pre():
    """Test task_cl_bump_pre."""
    result = task_cl_bump_pre()

    actions = result['actions']
    assert len(actions) == 3
    assert 'poetry run cz bump --changelog --prerelease' in str(actions[0])
    assert isinstance(actions[1][0], type(_move_cl))
    assert actions[2] == 'git push origin --tags --no-verify'
    params = result['params']
    assert len(params) == 1
    assert params[0]['name'] == 'prerelease'
    assert params[0]['short'] == 'p'


def _star_parser(section: str, path_md: Path) -> str:
    rating = int(_parse_var_comment(section)['rating'])
    return [f'RATING={rating}']


# FIXME: Fails and doesn't modify the file...
@pytest.mark.CURRENT()
def test_write_autoformatted_md_sections(fix_test_cache):
    """Test write_autoformatted_md_sections."""
    path_md_file = TEST_DATA_DIR / 'sample_doc_files' / 'README.md'
    path_new_readme = fix_test_cache / path_md_file.name
    shutil.copyfile(path_md_file, path_new_readme)
    #
    paths_original = DG.doc.paths_md
    lookup_original = DG.doc.handler_lookup
    #
    DG.doc.paths_md = [path_new_readme]
    DG.doc.handler_lookup = {
        'rating': _star_parser,
    }

    write_autoformatted_md_sections()  # act

    text = path_new_readme.read_text()
    assert '\n<!-- rating=' not in text
    assert '\n\nRATING=4\n\n' in text
    assert """<!-- {cts} name_image=TBD.img; (User can specify image name) -->
<!-- AUTO-Image -->
<!-- Capture image -->
<!-- /AUTO-Image {cte} -->""" in text
    #
    DG.doc.paths_md = paths_original
    DG.doc.handler_lookup = lookup_original


def test_task_serve_docs():
    """Test task_serve_docs."""
    result = task_serve_docs()

    actions = result['actions']
    assert len(actions) == 2
    assert isinstance(actions[0][0], type(webbrowser.open))
    assert len(actions[0][1]) == 1
    assert actions[0][1][0].startswith('http://localhost')
    assert str(actions[1]).endswith('mkdocs serve --dirtyreload')


def test_task_deploy():
    """Test task_deploy."""
    result = task_deploy()

    actions = result['actions']
    assert len(actions) == 1
    assert str(actions[0]).endswith('mkdocs gh-deploy')


def test_task_open_docs():
    """Test task_open_docs."""
    result = task_open_docs()

    actions = result['actions']
    assert len(actions) == 1
    assert isinstance(actions[0][0], type(webbrowser.open))
    assert len(actions[0][1]) == 1
    assert actions[0][1][0].name == 'index.html'
