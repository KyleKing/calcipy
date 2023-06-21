"""Find Files."""

from collections import defaultdict
from pathlib import Path

from beartype import beartype
from beartype.typing import Dict, List, Optional
from corallium.log import logger
from corallium.shell import capture_shell


@beartype
def _zsplit(stdout: str) -> List[str]:
    """Split output from git when used with `-z`."""
    return [item for item in stdout.split('\0') if item]


@beartype
def _get_all_files(*, cwd: Path) -> List[str]:
    """Get all files using git. Modified `pre_commit.git.get_all_files` to accept `cwd`.

    https://github.com/pre-commit/pre-commit/blob/488b1999f36cac62b6b0d9bc8eae99418ae5c226/pre_commit/git.py#L153

    Args:
        cwd: current working directory to pass to `subprocess.Popen`

    Returns:
        List[str]: list of all file paths relative to the `cwd`

    """
    return _zsplit(capture_shell('git ls-files -z', cwd=cwd))


@beartype
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
        for _fp in rel_filepaths:
            pth = Path(_fp).resolve()
            if not any(pth.match(pat) for pat in ignore_patterns):
                matches.append(_fp)
        return matches
    return rel_filepaths


@beartype
def find_project_files(path_project: Path, ignore_patterns: List[str]) -> List[Path]:
    """Find project files in git version control.

    > Note: uses the relative project directory and verifies that each file exists

    Args:
        path_project: Path to the project directory
        ignore_patterns: glob ignore patterns

    Returns:
        Dict[str, List[Path]]: where keys are the suffix (without leading dot) and values the list of paths

    """
    file_paths = []
    rel_filepaths = _get_all_files(cwd=path_project)
    filtered_rel_files = _filter_files(rel_filepaths=rel_filepaths, ignore_patterns=ignore_patterns)
    for rel_file in filtered_rel_files:
        path_file = path_project / rel_file
        if path_file.is_file():
            file_paths.append(path_file)
        else:  # pragma: no cover
            logger.warning('Could not find the specified file', path_file=path_file)
    return file_paths


# TODO: Consider adding a configuration item for ignore_patterns
@beartype
def find_project_files_by_suffix(
    path_project: Path, *, ignore_patterns: Optional[List[str]] = None,
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
