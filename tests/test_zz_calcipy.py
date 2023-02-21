"""Final test alphabetically (zz) to catch general integration cases."""

from pathlib import Path

from calcipy import __version__

# PLANNED: Move to the shared package
try:
    import tomllib  # pyright: ignore[reportMissingImports]
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore[no-redef]


def test_version():
    """Check that PyProject and package __version__ are equivalent."""
    data = Path('pyproject.toml').read_text(encoding='utf-8')

    result = tomllib.loads(data)['tool']['poetry']['version']

    assert result == __version__
