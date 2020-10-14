"""General DoIt Utilities and Requirements."""

import webbrowser
from pathlib import Path

import toml
from icecream import ic

# ----------------------------------------------------------------------------------------------------------------------
# Global Variables


class DoItGlobals:
    """Global Variables for DoIt."""

    dash_dev_dir = Path(__file__).parent
    """Dash Dev package directory that contains."""

    flake8_path = dash_dev_dir / '../.flake8'
    """Path to flake8 file. Default is for the flake8 file from dash_dev."""

    path_gitchangelog = dash_dev_dir / '.gitchangelog.rc'
    """Path to isort file. Default is for the isort file from dash_dev."""

    source_path = None
    """Current directory for working project. Set in `set_paths`."""

    toml_path = None
    """Path to `pyproject.toml` file for working project. Set in `set_paths`."""

    pkg_name = None
    """Name of the current package based on the poetry configuration file. Set in `set_paths`."""

    doc_dir = None
    """Path to documentation directory for working project. Set in `set_paths`."""

    staging_dir = None
    """Path to staging directory for working project. Set in `set_paths`."""

    src_examples_dir = None
    """Path to example code directory for working project. Set in `set_paths`."""

    tmp_examples_dir = None
    """Path to temporary directory to move examples while creating documentation. Set in `set_paths`."""

    def set_paths(self, source_path):
        """Set data members based on working directory.

        Args:
            source_path: path to working directory (ex: `Path(__file__).parent`)

        """
        self.source_path = source_path

        self.toml_path = self.source_path / 'pyproject.toml'
        self.pkg_name = toml.load(self.toml_path)['tool']['poetry']['name']

        self.doc_dir = self.source_path / 'docs'
        self.staging_dir = self.doc_dir / self.pkg_name
        self.staging_dir.mkdir(exist_ok=True, parents=True)

        self.src_examples_dir = self.source_path / 'tests/examples'
        self.tmp_examples_dir = self.source_path / f'{self.pkg_name}/0EX'
        if not self.src_examples_dir.is_dir():
            self.src_examples_dir = None  # If the directory is not present, disable this functionality


DIG = DoItGlobals()
"""Global DoIt Globals class used to manage global variables."""

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
