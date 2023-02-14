"""General task utilities."""

from beartype import beartype
from pathlib import Path
from functools import lru_cache

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef]

# FYI: Actively adapting from DIG: https://github.com/KyleKing/calcipy/blob/4b102c8a8c752bae0804860f06b7f85ebcba6c3f/calcipy/doit_tasks/doit_globals.py#L165-L181

@lru_cache(maxsize=1)
@beartype
def read_poetry_config() -> dict:
	"""Read the 'pyproject.toml' file once."""
	toml_path = Path('pyproject.toml')
	try:
		pyproject_txt = toml_path.read_text()
	except Exception:
		raise RuntimeError(f"This task must be run from a directory that contains a '{toml_path.name}' for poetry, but the command could not locate: {toml_path}")
	return tomllib.loads(pyproject_txt)['tool']['poetry']


@lru_cache(maxsize=1)
@beartype
def read_package_name() -> str:
	"""Read the package name once."""
	poetry_config = read_poetry_config()
	return poetry_config['name']
