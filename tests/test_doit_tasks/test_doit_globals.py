"""Test doit_tasks/doit_globals.py."""

from pathlib import Path

from calcipy.doit_tasks.doit_globals import DocConfig


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