"""nox with uv backend configuration.

Modern nox configuration using uv as the virtual environment backend.
Automatically discovers Python versions from mise.toml, mise.lock, or .tool-versions.

[Useful snippets from docs](https://nox.thea.codes/en/stable/usage.html)

```sh
# List all sessions
nox -l

# Run tests for all Python versions
nox -s tests

# Run tests for specific Python version
nox -s tests-3.11

# Run with specific Python versions only
nox --python 3.10 3.11

# Filter sessions by keyword
nox -k tests
```

"""

import shlex
from functools import lru_cache

from beartype.typing import Any, Dict, List, Union
from corallium.file_helpers import get_tool_versions, read_package_name, read_pyproject
from nox import Session as NoxSession
from nox import session as nox_session


@lru_cache(maxsize=1)
def _get_pythons() -> List[str]:
    """Return python versions from supported configuration files."""
    return [*{str(ver) for ver in get_tool_versions()['python']}]


def _has_ci_group(pyproject_data: Union[Dict[str, Any], None] = None) -> bool:
    """Check if pyproject.toml has a 'ci' dependency group.

    Args:
        pyproject_data: Optional pyproject data for testing

    Returns:
        bool: True if 'ci' group exists

    """
    pyproject = read_pyproject() if pyproject_data is None else pyproject_data
    return bool(pyproject.get('dependency-groups', {}).get('ci'))


def _install_local(session: NoxSession) -> None:  # pragma: no cover
    """Install project dependencies using uv sync.

    Uses uv's dependency groups and extras for isolation.
    For calcipy itself, installs all extras to test the full package.
    For other projects, installs test extras and ci group if available.

    Modern pattern (2026): Use uv sync with --group flag to install dependency groups,
    which automatically handles dependencies from uv.lock if present.

    """
    sync_args = ['uv', 'sync']

    if read_package_name() == 'calcipy':
        # Install all extras for comprehensive testing of calcipy itself
        sync_args.append('--all-extras')
    else:
        # Install test extras for downstream projects
        sync_args.extend(['--extra=test'])

    # Add ci dependency group if it exists
    if _has_ci_group():
        sync_args.extend(['--group=ci', '--no-default-groups'])

    session.run_install(
        *sync_args,
        env={'UV_PROJECT_ENVIRONMENT': session.virtualenv.location},
    )


@nox_session(venv_backend='uv', python=_get_pythons(), reuse_venv=True)
def tests(session: NoxSession) -> None:  # pragma: no cover
    """Run pytest for all configured Python versions.

    Python versions are automatically discovered from:
    1. mise.lock (if present)
    2. mise.toml (if present)
    3. .tool-versions (fallback)

    Run all versions: nox -s tests
    Run specific version: nox -s tests-3.11
    """
    _install_local(session)
    session.run(
        *shlex.split('pytest ./tests'),
        stdout=True,
        env={'RUNTIME_TYPE_CHECKING_MODE': 'WARNING'},
    )
