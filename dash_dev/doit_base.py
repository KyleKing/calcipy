"""General DoIt Utilities and Requirements."""

import shutil
import webbrowser
from pathlib import Path

import toml
from icecream import ic

# ----------------------------------------------------------------------------------------------------------------------
# Global Variables


class DoItGlobals:
    """Global Variables for DoIt."""

    dash_dev_dir = Path(__file__).parent
    """The dash_dev directory (may be within `.venv`)."""

    flake8_path = dash_dev_dir / '../.flake8'
    """Path to flake8 file. Default is for the flake8 file from dash_dev."""

    path_gitchangelog = dash_dev_dir / '.gitchangelog.rc'
    """Path to isort file. Default is for the isort file from dash_dev."""

    lint_paths = []
    """Current directory for source code (working project). Set in `set_paths`."""

    external_doc_dirs = ['examples', 'scripts', 'tests']
    """List of subdir names relative to `source_path` containing Python code that should be in the documentation.

    Note: for nested directories, combine subdirectires into a single string, ex: `('examples', 'examples/sub_dir')`

    """

    source_path = None
    """Current directory for source code (working project). Set in `set_paths`."""

    test_path = None
    """Current directory for tests directory. Resolved as '`source_path`/tests' in `set_paths`."""

    toml_path = None
    """Path to `pyproject.toml` file for working project. Set in `set_paths`."""

    pkg_name = None
    """Name of the current package based on the poetry configuration file. Set in `set_paths`."""

    doc_dir = None
    """Path to documentation directory for working project. Set in `set_paths`."""

    coverage_path = None
    """Path to the coverage index.html file. Set in `set_paths`."""

    test_report_path = None
    """Path to the test report file. Set in `set_paths`."""

    src_examples_dir = None
    """Path to example code directory for working project. Set in `set_paths`."""

    tmp_examples_dir = None
    """Path to temporary directory to move examples while creating documentation. Set in `set_paths`."""

    def set_paths(self, *, pkg_name=None, source_path=None, doc_dir=None):
        """Set data members based on working directory.

        Args:
            pkg_name: Package name or defaults to value from toml
            source_path: Source directory Path, typically 'src' or ''
            doc_dir: Destination directory for project documentation

        Raises:
            RuntimeError: if package name includes dashes

        """
        self.source_path = Path.cwd() if source_path is None else source_path

        # Define the output directory with relevant subdirectories
        self.test_path = self.source_path / 'tests'
        self.doc_dir = self.source_path / 'docs' if doc_dir is None else doc_dir
        ensure_dir(self.doc_dir)
        self.coverage_path = self.doc_dir / 'cov_html/index.html'
        self.test_report_path = self.doc_dir / 'test_report.html'

        self.toml_path = self.source_path / 'pyproject.toml'
        if not self.toml_path.is_file():
            raise RuntimeError(f'Could not find {self.toml_path.name}. Check that the {self.source_path} is correct')
        self.pkg_name = toml.load(self.toml_path)['tool']['poetry']['name']
        if '-' in self.pkg_name:
            raise RuntimeError(f'Replace dashes in name with underscores ({self.pkg_name}) in {self.toml_path}')

        # TODO: Make more generic
        self.src_examples_dir = self.source_path / 'tests/examples'
        self.tmp_examples_dir = self.source_path / f'{self.pkg_name}/0EX'
        if not self.src_examples_dir.is_dir():
            self.src_examples_dir = None  # If the directory is not present, disable this functionality

        # Create list of directories and paths to isort and format
        subdirs = [self.pkg_name] + self.external_doc_dirs
        self.lint_paths = [self.source_path / subdir for subdir in subdirs]
        self.lint_paths.extend([self.test_path] + [*self.source_path.glob('*.py')])
        self.lint_paths = {lint_path for lint_path in self.lint_paths if lint_path.exists()}


DIG = DoItGlobals()
"""Global DoIt Globals class used to manage global variables."""

# ----------------------------------------------------------------------------------------------------------------------
# Manage Directories


def delete_dir(dir_path):
    """Delete the specified directory from a DoIt task.

    Args:
        dir_path: Path to directory to delete

    """
    if dir_path.is_dir():
        shutil.rmtree(dir_path)
    return  # Indicates that action completed when called from DoIt task


def ensure_dir(dir_path):
    """Make sure that the specified dir_path exists and create any missing folders from a DoIt task.

    Args:
        dir_path: Path to directory that needs to exists

    """
    dir_path.mkdir(parents=True, exist_ok=True)
    return  # Indicates that action completed when called from DoIt task


# ----------------------------------------------------------------------------------------------------------------------
# General Utilities


def show_cmd(task):
    """For debugging, log the full command to the console.

    Args:
        task: task dictionary passed by DoIt

    Returns:
        str: describing the sequence of actions

    """
    actions = ''.join([f'\n\t{act}' for act in task.actions])
    return f'{task.name} > [{actions}\n]\n'


def debug_action(actions, verbosity=2):
    """Enable verbose logging for the specified actions.

    Args:
        actions: list of DoIt actions
        verbosity: 2 is maximum, while 0 is disabled. Default is 2

    Returns:
        dict: keys `actions`, `title`, and `verbosity` for dict: DoIt task

    """
    return {
        'actions': actions,
        'title': show_cmd,
        'verbosity': verbosity,
    }


def open_in_browser(file_path):
    """Open the path in the default web browser.

    Args:
        file_path: Path to file

    """
    webbrowser.open(Path(file_path).as_uri())


def if_found_unlink(file_path):
    """Remove file if it exists. Function is intended to a DoIt action.

    Args:
        file_path: Path to file to remove

    """
    if file_path.is_file():
        file_path.unlink()


def echo(msg):
    """Wrap the system print command.

    Args:
        msg: string to `print`

    """
    print(msg)  # noqa: T001


# ----------------------------------------------------------------------------------------------------------------------
# Manage Requirements


def task_export_req():
    """Create a `requirements.txt` file for non-Poetry users and for Github security tools.

    Returns:
        dict: DoIt task

    """
    req_path = DIG.toml_path.parent / 'requirements.txt'
    return debug_action([f'poetry export -f {req_path.name} -o "{req_path}" --without-hashes --dev'])


def dump_pur_results(pur_path):
    """Write the contents of the `pur` output file to STDOUT with icecream.

    Args:
        pur_path: Path to the pur output text file

    """
    ic(pur_path.read_text())


def task_check_req():
    """Use pur to check for the latest versions of available packages.

    Returns:
        dict: DoIt task

    """
    req_path = DIG.toml_path.parent / 'requirements.txt'
    pur_path = DIG.toml_path.parent / 'tmp.txt'
    return debug_action([
        f'poetry run pur -r "{req_path}" > "{pur_path}"',
        (dump_pur_results, (pur_path, )),
        (Path(pur_path).unlink, ),
    ])
