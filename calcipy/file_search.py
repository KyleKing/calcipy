"""Find Files."""

from collections import defaultdict
from contextlib import suppress
from pathlib import Path
from subprocess import CalledProcessError  # noqa: S404

from beartype.typing import Dict, List, Optional, Tuple
from corallium.log import LOGGER
from corallium.shell import capture_shell


def _zsplit(stdout: str) -> List[str]:
    """Split output from git when used with `-z`."""
    return [item for item in stdout.split('\0') if item]


def _walk_files(*, cwd: Path) -> List[str]:
    """Get all files using recursive filesystem walk.

    Args:
        cwd: directory to search recursively

    Returns:
        List[str]: list of all file paths relative to cwd

    """
    files = []
    for path in cwd.rglob('*'):
        if path.is_file():
            try:
                rel_path = path.relative_to(cwd)
                files.append(rel_path.as_posix())
            except ValueError:
                LOGGER.debug('Skipping path outside cwd', path=path, cwd=cwd)
    return sorted(files)


def _get_default_ignore_patterns() -> List[str]:
    """Default ignore patterns for filesystem walk (when git unavailable)."""
    return [
        # VCS directories
        '**/.git/**',
        '**/.jj/**',
        # Python build artifacts
        '**/__pycache__/**',
        '**/*.pyc',
        '**/*.egg-info/**',
        '**/dist/**',
        '**/build/**',
        # Python test/cache directories
        '**/.pytest_cache/**',
        '**/.mypy_cache/**',
        '**/.ruff_cache/**',
        '**/.nox/**',
        '**/.tox/**',
        '**/htmlcov/**',
        '**/.coverage*',
        # Python virtual environments
        '**/.venv/**',
        '**/venv/**',
        # JavaScript/Node
        '**/node_modules/**',
    ]


def _get_all_files(*, cwd: Path) -> Tuple[List[str], bool]:
    """Get all files using git, falling back to filesystem walk.

    Args:
        cwd: current working directory to pass to `subprocess.Popen`

    Returns:
        Tuple[List[str], bool]: (file paths, used_git)

    """
    with suppress(CalledProcessError):
        return _zsplit(capture_shell('git ls-files -z', cwd=cwd)), True

    LOGGER.debug('Git not available, using filesystem walk', cwd=cwd)
    return _walk_files(cwd=cwd), False


def _filter_files(rel_filepaths: List[str], ignore_patterns: List[str]) -> List[str]:
    """Filter a list of string file paths with specified ignore patterns in glob syntax.

    Args:
        rel_filepaths: list of string file paths
        ignore_patterns: glob ignore patterns

    Returns:
        List[str]: list of all non-ignored file path names

    """
    if ignore_patterns:
        matches = []
        for fp in rel_filepaths:
            pth = Path(fp).resolve()
            if not any(pth.match(pat) for pat in ignore_patterns):
                matches.append(fp)
        return matches
    return rel_filepaths


def find_project_files(path_project: Path, ignore_patterns: List[str]) -> List[Path]:
    """Find project files in git version control or via filesystem walk.

    > Note: uses the relative project directory and verifies that each file exists

    Args:
        path_project: Path to the project directory
        ignore_patterns: glob ignore patterns

    Returns:
        Dict[str, List[Path]]: where keys are the suffix (without leading dot) and values the list of paths

    """
    file_paths = []
    rel_filepaths, used_git = _get_all_files(cwd=path_project)

    # When not using git, apply default ignores if no patterns specified
    effective_patterns = ignore_patterns
    if not used_git and not ignore_patterns:
        effective_patterns = _get_default_ignore_patterns()
        LOGGER.info(
            'Using default ignore patterns for filesystem walk. Specify --ignore-patterns to customize.',
            pattern_count=len(effective_patterns),
        )

    filtered_rel_files = _filter_files(
        rel_filepaths=rel_filepaths,
        ignore_patterns=effective_patterns,
    )
    for rel_file in filtered_rel_files:
        path_file = path_project / rel_file
        if path_file.is_file():
            file_paths.append(path_file)
        else:  # pragma: no cover
            LOGGER.warning('Could not find the specified file', path_file=path_file)
    return file_paths


def find_project_files_by_suffix(
    path_project: Path,
    *,
    ignore_patterns: Optional[List[str]] = None,
) -> Dict[str, List[Path]]:
    """Find project files in git version control.

    > Note: uses the relative project directory and verifies that each file exists

    Args:
        path_project: Path to the project directory
        ignore_patterns: glob ignore patterns

    Returns:
        Dict[str, List[Path]]: where keys are the suffix (without leading dot) and values the list of paths

    """
    file_lookup: Dict[str, List[Path]] = defaultdict(list)
    for path_file in find_project_files(path_project, ignore_patterns or []):
        file_lookup[path_file.suffix.lstrip('.')].append(path_file)
    return dict(file_lookup)
