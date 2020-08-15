"""Final test alphabetically (zz) to catch general integration cases."""

import toml

from dash_dev import __version__


def test_version():  # noqa: AAA01
    """Check that PyProject and __version__ are equivalent."""
    assert toml.load('pyproject.toml')['tool']['poetry']['version'] == __version__
