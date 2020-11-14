"""General DoIt Utilities and Requirements."""

import shutil
import webbrowser
from pathlib import Path
from typing import Any, Callable, Dict, List, NewType, Optional, Sequence, Tuple, Union

import toml
from loguru import logger

from ..log_helpers import log_action, log_fun

# TODO: Show dodo.py in the documentation
# TODO: Show README.md in the documentation (may need to update paths?)
# TODO: Replace src_examples_dir and make more generic to specify code to include in documentation
# TODO: Show table of contents in __init__.py file. Use ast:
#   https://www.ecosia.org/search?q=ast+find+all+functions+and+classes+in+python+package

# ----------------------------------------------------------------------------------------------------------------------
# Global Variables

DoItTask = NewType('DoItTask', Dict[str, Union[str, Tuple[Callable, Sequence]]])  # noqa: ECE001
"""DoIt task type for annotations."""


class DoItGlobals:
    """Global Variables for DoIt."""

    dash_dev_dir: Path = Path(__file__).parents[1]
    """The dash_dev directory (may be within `.venv`)."""

    flake8_path: Optional[Path] = None
    """Path to flake8 file. Set in `set_paths()` based on source_path """

    path_gitchangelog: Path = dash_dev_dir / '.gitchangelog.rc'
    """Path to isort file. Default is for the isort file from dash_dev."""

    lint_paths = []
    """Current directory for source code (working project). Set in `set_paths`."""

    excluded_files = ['__init__.py']
    """List of excluded filenames."""

    external_doc_dirs = ['examples', 'scripts', 'tests']
    """List of subdir names relative to `source_path` containing Python code that should be in the documentation.

    Note: for nested directories, combine subdirectires into a single string, ex: `('examples', 'examples/sub_dir')`

    """

    source_path: Optional[Path] = None
    """Current directory for source code (working project). Set in `set_paths`."""

    test_path: Optional[Path] = None
    """Current directory for tests directory. Resolved as '`source_path`/tests' in `set_paths`."""

    toml_path: Optional[Path] = None
    """Path to `pyproject.toml` file for working project. Set in `set_paths`."""

    pkg_name: Optional[str] = None
    """Name of the current package based on the poetry configuration file. Set in `set_paths`."""

    doc_dir: Optional[Path] = None
    """Path to documentation directory for working project. Set in `set_paths`."""

    coverage_path: Optional[Path] = None
    """Path to the coverage index.html file. Set in `set_paths`."""

    test_report_path: Optional[Path] = None
    """Path to the test report file. Set in `set_paths`."""

    src_examples_dir: Optional[Path] = None
    """Path to example code directory for working project. Set in `set_paths`."""

    tmp_examples_dir: Optional[Path] = None
    """Path to temporary directory to move examples while creating documentation. Set in `set_paths`."""

    # PLANNED: Document
    template_dir = None
    pkg_version = None

    def set_paths(self, *, pkg_name: Optional[str] = None, source_path: Optional[Path] = None,
                  doc_dir: Optional[Path] = None) -> None:
        """Set data members based on working directory.

        Args:
            pkg_name: Package name or defaults to value from toml
            source_path: Source directory Path, typically 'src' or ''
            doc_dir: Destination directory for project documentation

        Raises:
            RuntimeError: if package name includes dashes

        """
        self.source_path = Path.cwd() if source_path is None else source_path
        logger.info(f'Setting DIG paths for {pkg_name} at {self.source_path}', pkg_name=pkg_name,
                    source_path=source_path, self_source_path=self.source_path, doc_dir=doc_dir)

        # Define the output directory with relevant sub_directories
        self.test_path = self.source_path / 'tests'
        self.doc_dir = self.source_path / 'docs' if doc_dir is None else doc_dir
        self.template_dir = self.doc_dir / 'templates'
        ensure_dir(self.template_dir)
        self.coverage_path = self.doc_dir / 'cov_html/index.html'
        self.test_report_path = self.doc_dir / 'test_report.html'
        self.flake8_path = self.source_path / '.flake8'

        self.toml_path = self.source_path / 'pyproject.toml'
        if not self.toml_path.is_file():
            raise RuntimeError(f'Could not find {self.toml_path.name}. Check that the {self.source_path} is correct')
        poetry_config = toml.load(self.toml_path)['tool']['poetry']
        self.pkg_version = poetry_config['version']
        self.pkg_name = poetry_config['name']
        if '-' in self.pkg_name:
            raise RuntimeError(f'Replace dashes in name with underscores ({self.pkg_name}) in {self.toml_path}')

        self.src_examples_dir = self.source_path / 'tests/examples'
        self.tmp_examples_dir = self.source_path / f'{self.pkg_name}/0EX'
        if not self.src_examples_dir.is_dir():
            self.src_examples_dir = None  # If the directory is not present, deactivate this functionality

        # Create list of directories and paths to isort and format
        sub_dirs = [self.pkg_name] + self.external_doc_dirs
        self.lint_paths = [self.source_path / subdir for subdir in sub_dirs]
        self.lint_paths.extend([self.test_path] + [*self.source_path.glob('*.py')])
        self.lint_paths = {lint_path for lint_path in self.lint_paths if lint_path.exists()}

        logger.warning('Completed DIG initialization, but this needs to be decomposed.'
                       'Additionally, all of the paths should be logged for troubleshooting if needed')


DIG = DoItGlobals()
"""Global DoIt Globals class used to manage global variables."""

# ----------------------------------------------------------------------------------------------------------------------
# Really General...


@log_fun
def read_lines(file_path: Path) -> List[str]:
    """Read a file and split on newlines for later parsing.

    Args:
        file_path: path to the file

    Returns:
        List[str]: lines of text as list

    """
    if file_path.is_file():
        return file_path.read_text().split('\n')
    return []


# ----------------------------------------------------------------------------------------------------------------------
# Manage Directories


def delete_dir(dir_path: Path) -> None:
    """Delete the specified directory from a DoIt task.

    Args:
        dir_path: Path to directory to delete

    """
    if dir_path.is_dir():
        logger.info(f'Deleting `{dir_path}`', dir_path=dir_path)
        shutil.rmtree(dir_path)


@log_fun
def ensure_dir(dir_path: Path) -> None:
    """Make sure that the specified dir_path exists and create any missing folders from a DoIt task.

    Args:
        dir_path: Path to directory that needs to exists

    """
    with log_action(f'Create `{dir_path}`'):
        dir_path.mkdir(parents=True, exist_ok=True)


# ----------------------------------------------------------------------------------------------------------------------
# General DoIt Utilities


@log_fun
def _show_cmd(task: DoItTask) -> str:
    """For debugging, log the full command to the console.

    Args:
        task: DoIt task

    Returns:
        str: describing the sequence of actions

    """
    actions = ''.join([f'\n\t{act}' for act in task.actions])
    return f'{task.name} > [{actions}\n]\n'


@log_fun
def debug_task(actions: Sequence[Any], verbosity: int = 2) -> DoItTask:
    """Activate verbose logging for the specified actions.

    Args:
        actions: list of DoIt actions
        verbosity: 2 is maximum, while 0 is deactivated. Default is 2

    Returns:
        DoItTask: DoIt task

    """
    task = {
        'actions': actions,
        'title': _show_cmd,
        'verbosity': verbosity,
    }
    logger.info('Created task', task=task)
    return task


@log_fun
def debug_action(actions: Sequence[Any], verbosity: int = 2) -> DoItTask:  # noqa
    import warnings
    warnings.warn('debug_action is deprecated. Replace with `debug_task`')
    return debug_task(actions, verbosity)


@log_fun
def echo(msg: str) -> None:
    """Wrap the system print command.

    Args:
        msg: string to write to STDOUT

    """
    print(msg)  # noqa: T001


@log_fun
def write_text(file_path: Path, text: str) -> None:
    """file_path.write_text wrapper for DoIt.

    Args:
        file_path: Path to the file
        text: string to write to file

    """
    file_path.write_text(text)


@log_fun
def open_in_browser(file_path: Path) -> None:
    """Open the path in the default web browser.

    Args:
        file_path: Path to file

    """
    webbrowser.open(Path(file_path).as_uri())


def if_found_unlink(file_path: Path) -> None:
    """Remove file if it exists. Function is intended to a DoIt action.

    Args:
        file_path: Path to file to remove

    """
    if file_path.is_file():
        logger.info(f'Deleting `{file_path}`', file_path=file_path)
        file_path.unlink()


# ----------------------------------------------------------------------------------------------------------------------
# Manage Requirements


@log_fun
def task_export_req() -> DoItTask:
    """Create a `requirements.txt` file for non-Poetry users and for Github security tools.

    Returns:
        DoItTask: DoIt task

    """
    req_path = DIG.toml_path.parent / 'requirements.txt'
    return debug_task([f'poetry export -f {req_path.name} -o "{req_path}" --without-hashes --dev'])
