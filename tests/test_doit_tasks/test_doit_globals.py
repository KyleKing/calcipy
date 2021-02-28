"""Test doit_tasks/doit_globals.py."""

from pathlib import Path
from typing import Any, List

from calcipy.doit_tasks.doit_globals import DocConfig, DoItGlobals

from ..configuration import PATH_TEST_PROJECT


def _get_public_props(obj: Any) -> List[str]:
    """Return the list of public props from an object."""
    return [prop for prop in dir(obj) if not prop.startswith('_')]


def test_dig_props():
    """Test the DIG global variable from DoItGlobals."""
    public_props = ['calcipy_dir', 'set_paths']
    settable_props = public_props + ['meta', 'ct', 'lint', 'test', 'doc']

    dig = DoItGlobals()  # act

    assert _get_public_props(dig) == sorted(public_props)
    dig.set_paths(path_project=PATH_TEST_PROJECT)
    assert _get_public_props(dig) == sorted(settable_props)


def test_dig_paths():
    """Test the DIG global variable from DoItGlobals."""
    dig = DoItGlobals()
    pkg_name = PATH_TEST_PROJECT.name
    path_out_base = PATH_TEST_PROJECT / 'releases'

    dig.set_paths(path_project=PATH_TEST_PROJECT)  # act

    # Test the properties set by default
    assert dig.calcipy_dir.name == 'calcipy'
    assert dig.lint.path_flake8 == PATH_TEST_PROJECT / '.flake8'
    # Test the properties set by set_paths
    assert dig.meta.path_project == PATH_TEST_PROJECT
    assert dig.meta.path_toml == PATH_TEST_PROJECT / 'pyproject.toml'
    assert dig.meta.pkg_name == pkg_name
    assert dig.doc.path_out == path_out_base / 'site'
    assert dig.test.path_out == path_out_base / 'tests'


def test_path_attr_base_path_resolver():
    """Test the _PathAttrBase class."""
    base_path = Path().resolve()

    doc = DocConfig(path_project=base_path)  # act

    assert doc.path_out.is_absolute()


# import pytest
# from calcipy.doit_tasks.doit_globals import TestingConfig
# Parametrize for path_project to be none or a path and show that both raise an error for different missing paths...
# >> RuntimeError: Missing keyword arguments for: path_out
# >> RuntimeError: Missing keyword arguments for: path_out, path_project
# def test_path_attr_base_path_verifier():
#     with pytest.raises(RuntimeError, tbd=''):
#         TestingConfig(path_project=None)
