"""Test doit_tasks/doit_globals.py."""

from pathlib import Path

from calcipy.doit_tasks.doit_globals import TestingConfig, create_dg, get_dg

from ..configuration import PATH_TEST_PROJECT


def test_dg_paths():
    """Test the DG global variable from DoitGlobals."""
    dg = create_dg(path_project=PATH_TEST_PROJECT)  # act

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

    doc = TestingConfig(path_project=base_path)  # act

    assert doc.path_out.is_absolute()


def test_doit_configurable():
    """Test configurable items from TOML file."""
    dg = get_dg()  # act

    dg.meta._shorten_path_lists()

    assert dg.meta.path_project.name == PATH_TEST_PROJECT.name
    assert dg.tags.tags == ['FIXME', 'TODO', 'PLANNED']  # noqa: T101, T103
    assert dg.tags.code_tag_summary_filename == 'CODE_TAG_SUMMARY.md'
    assert dg.test.path_out == PATH_TEST_PROJECT / 'releases/tests'
    assert dg.test.pythons == ['3.8', '3.9']
    assert dg.test.args_pytest == '-x -l --ff --nf -vv'
    assert dg.test.args_diff == '--fail-under=95 --compare-branch=origin/release'
    assert dg.doc.path_out == PATH_TEST_PROJECT / 'releases/site'
    assert dg.lint.path_flake8 == PATH_TEST_PROJECT / '.flake8'
    assert dg.lint.path_isort == PATH_TEST_PROJECT / '.isort.cfg'  # user-configured
    assert dg.lint.ignore_errors == ['T100', 'T101', 'T103']
