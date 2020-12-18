"""Test doit_helpers/doit_globals.py."""

from pathlib import Path

import pytest

from calcipy.doit_helpers.doit_globals import DocConfig, TestConfig


def test_path_attr_base_path_resolver():
    """Test the _PathAttrBase class."""
    base_path = Path().resolve()

    dp = DocConfig(path_source=base_path)  # act

    assert not DocConfig.path_changelog.is_absolute()
    assert dp.path_changelog.is_absolute()
    assert dp.path_changelog == base_path / DocConfig.path_changelog


# Parametrize for path_source to be none or a path and show that both raise an error for different missing paths...
# >> RuntimeError: Missing keyword arguments for: path_out
# >> RuntimeError: Missing keyword arguments for: path_out, path_source
# def test_path_attr_base_path_verifier():
#     with pytest.raises(RuntimeError, tbd=''):
#         TestConfig(path_source=None)
