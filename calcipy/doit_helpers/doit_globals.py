"""Global Variables for DoIt."""

from pathlib import Path
from typing import Callable, Dict, NewType, Optional, Sequence, Tuple, Union

import toml
from loguru import logger

from ..log_helpers import log_fun

# ----------------------------------------------------------------------------------------------------------------------
# Global Variables

DoItTask = NewType('DoItTask', Dict[str, Union[str, Tuple[Callable, Sequence]]])  # noqa: ECE001
"""DoIt task type for annotations."""


class DoItGlobals:
    """Global Variables for DoIt."""

    calcipy_dir: Path = Path(__file__).parents[1]
    """The calcipy directory (may be within `.venv`)."""

    flake8_path: Optional[Path] = None
    """Path to flake8 file. Set in `set_paths()` based on source_path """

    path_gitchangelog: Path = calcipy_dir / '.gitchangelog.rc'
    """Path to isort file. Default is for the isort file from calcipy."""

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

    @log_fun
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
        self.template_dir.mkdir(parents=True, exist_ok=True)
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
