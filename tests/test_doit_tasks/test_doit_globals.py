"""Test doit_tasks/doit_globals.py."""

from pathlib import Path
from typing import List

from calcipy.doit_tasks.doit_globals import DG, DocConfig, DoitGlobals

from ..configuration import PATH_TEST_PROJECT


def _get_public_props(obj) -> List[str]:
    """Return the list of public props from an object."""
    return [prop for prop in dir(obj) if not prop.startswith('_')]


def test_dg_props():
    """Test the DG global variable from DoitGlobals."""
    public_props = ['calcipy_dir', 'set_paths']
    settable_props = public_props + ['meta', 'ct', 'lint', 'test', 'doc']

    dg = DoitGlobals()  # act

    assert _get_public_props(dg) == sorted(public_props)
    dg.set_paths(path_project=PATH_TEST_PROJECT)
    assert _get_public_props(dg) == sorted(settable_props)


def test_dg_paths():
    """Test the DG global variable from DoitGlobals."""
    dg = DoitGlobals()

    dg.set_paths(path_project=PATH_TEST_PROJECT)  # act

    # Test the properties set by default
    assert dg.calcipy_dir.name == 'calcipy'
    assert dg.lint.path_flake8 == PATH_TEST_PROJECT / '.flake8'
    # Test the properties set by set_paths
    assert dg.meta.path_project == PATH_TEST_PROJECT
    assert dg.meta.path_toml == PATH_TEST_PROJECT / 'pyproject.toml'
    assert dg.meta.pkg_name == 'test_project'
    path_out_base = PATH_TEST_PROJECT / 'releases'
    assert dg.doc.path_out == path_out_base / 'site'
    assert dg.test.path_out == path_out_base / 'tests'


def test_path_attr_base_path_resolver():
    """Test the _PathAttrBase class."""
    base_path = Path().resolve()

    doc = DocConfig(path_project=base_path)  # act

    assert doc.path_out.is_absolute()


def test_doit_configurable():
    """Test configurable items from TOML file."""
    dg = DG  # act

    assert dg.ct.tags == ['FIXME', 'TODO', 'PLANNED']  # noqa: T101, T103
    assert dg.ct.code_tag_summary_filename == 'CODE_TAG_SUMMARY.md'
    assert dg.test.path_out == PATH_TEST_PROJECT / 'releases/tests'
    assert dg.test.pythons == ['3.8', '3.9']
    assert dg.test.args_pytest == '-x -l --ff --nf -vv'
    assert dg.test.args_diff == '--fail-under=95 --compare-branch=origin/release'
    assert dg.doc.path_out == PATH_TEST_PROJECT / 'releases/site'
    assert dg.lint.path_flake8 == PATH_TEST_PROJECT / '.flake8'
    assert dg.lint.path_isort == PATH_TEST_PROJECT / '.isort.cfg'
    assert dg.lint.ignore_errors == ['T100', 'T101', 'T103']
