"""Test doit_tasks/doit_globals.py."""

from pathlib import Path
from typing import Any, List

from calcipy.doit_tasks.doit_globals import DocConfig, DoItGlobals

from ..configuration import DIG_CWD


def _get_public_props(obj: Any) -> List[str]:
    """Return the list of public props from an object."""
    return [prop for prop in dir(obj) if not prop.startswith('_')]


def test_dig_props():
    """Test the DIG global variable from DoItGlobals."""
    public_props = ['calcipy_dir', 'set_paths']
    settable_props = public_props + ['meta', 'lint', 'test', 'doc']

    dig = DoItGlobals()  # act

    assert _get_public_props(dig) == sorted(public_props)
    dig.set_paths(path_source=DIG_CWD)
    assert _get_public_props(dig) == sorted(settable_props)


def test_dig_paths():
    """Test the DIG global variable from DoItGlobals."""
    dig = DoItGlobals()
    pkg_name = DIG_CWD.name
    path_out_base = DIG_CWD / 'releases'

    dig.set_paths(path_source=DIG_CWD)  # act

    # Test the properties set by default
    assert dig.calcipy_dir.name == 'calcipy'
    assert dig.lint.path_flake8 == DIG_CWD / '.flake8'
    # Test the properties set by set_paths
    assert dig.meta.path_source == DIG_CWD
    assert dig.meta.path_toml == DIG_CWD / 'pyproject.toml'
    assert dig.meta.pkg_name == pkg_name
    assert dig.doc.path_out == path_out_base / 'site'
    assert dig.test.path_out == path_out_base / 'tests'


def test_path_attr_base_path_resolver():
    """Test the _PathAttrBase class."""
    base_path = Path().resolve()

    doc = DocConfig(path_source=base_path)  # act

    assert doc.path_out.is_absolute()


# import pytest
# from calcipy.doit_tasks.doit_globals import TestingConfig
# Parametrize for path_source to be none or a path and show that both raise an error for different missing paths...
# >> RuntimeError: Missing keyword arguments for: path_out
# >> RuntimeError: Missing keyword arguments for: path_out, path_source
# def test_path_attr_base_path_verifier():
#     with pytest.raises(RuntimeError, tbd=''):
#         TestingConfig(path_source=None)
