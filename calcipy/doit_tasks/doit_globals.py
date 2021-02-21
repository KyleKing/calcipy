"""Global Variables for doit."""

import inspect
import warnings
from functools import partial
from pathlib import Path
from typing import Any, Callable, Dict, List, NewType, Optional, Sequence, Tuple, Union

import attr
from loguru import logger

from ..log_helpers import log_fun

try:
    import toml
except ImportError:
    toml = None

_DOIT_TASK_IMPORT_ERROR = 'User must install the optional calcipy extra "dev" to utilize "doit_tasks"'
"""Standard error message when an optional import is not available. Raise with RuntimeError."""

# ----------------------------------------------------------------------------------------------------------------------
# Global Variables

DoItTask = NewType('DoItTask', Dict[str, Union[str, Tuple[Callable, Sequence]]])  # noqa: ECE001
"""doit task type for annotations."""


def _member_filter(member: Any, instance_type: Any) -> bool:
    """Return True if the member matches the filters.

    Args:
        member: class data- or method-member
        instance_type: optional instance type

    Returns:
        bool: True if the member matches the applied filter

    """
    return (instance_type is None or isinstance(member, instance_type))


def _get_members(cls: object, prefix: Optional[str], **kwargs: Any) -> List[Tuple[str, Callable]]:
    """Return the members that match the parameters.

    Example to return all methods that start with `do_`: `_get_members(cls, instance_type=Callable, prefix='do_')`

    Args:
        cls: class
        prefix: optional string prefix to check starts with
        **kwargs: keyword arguments passed to `_member_filter`

    Returns:
        List[Tuple[str, Callable]]: filtered members from the class

    """
    members = inspect.getmembers(cls, predicate=partial(_member_filter, **kwargs))
    if prefix:
        members = [(name, member) for (name, member) in members if name.startswith(prefix)]
    return members  # noqa: R504


def _verify_initialized_paths(cls: object) -> None:
    """Verify that all paths are not None.

    WARN: will not raise on error the class attribute

    Args:
        cls: class

    Raises:
        RuntimeError: if any paths are None

    """
    logger.info(f'Class: {cls}')
    missing = [name for name, _m in _get_members(cls, instance_type=type(None), prefix='path_')]
    if missing:
        kwargs = ', '.join(missing)
        raise RuntimeError(f'Missing keyword arguments for: {kwargs}')


def _resolve_class_paths(cls: object, base_path: Path) -> None:
    """Resolve all partial paths with the specified base path.

    WARN: will mutate the class attribute

    Args:
        cls: class
        base_path: base path to apply to all found relative paths

    """
    logger.info(f'Class: {cls}')
    for name, path_raw in _get_members(cls, instance_type=type(Path()), prefix=None):
        if not path_raw.is_absolute():
            setattr(cls, name, base_path / path_raw)
            logger.debug(f'Mutated: self.{name}={path_raw} (now: {getattr(cls, name)})')


_DEF_EXCLUDE = [*map(Path, ['__init__.py'])]
"""Default list of excluded filenames."""


@attr.s(auto_attribs=True, kw_only=True)
class _PathAttrBase:  # noqa: H601

    path_project: Path
    """Path to the package directory."""

    def __attrs_post_init__(self) -> None:
        """Initialize full paths with the package base directory if necessary.

        Raises:
            RuntimeError: if any paths are None

        """
        if self.path_project is None:
            raise RuntimeError('Missing keyword argument "path_project"')
        _resolve_class_paths(self, self.path_project)
        _verify_initialized_paths(self)


@attr.s(auto_attribs=True, kw_only=True)
class PackageMeta(_PathAttrBase):  # noqa: H601
    """Package Meta-Information."""

    path_toml: Path = Path('pyproject.toml')
    """Path to the poetry toml file."""

    pkg_name: str = attr.ib(init=False)
    """Package string name."""

    pkg_version: str = attr.ib(init=False)
    """Package version."""

    def __attrs_post_init__(self) -> None:
        """Finish initializing class attributes.

        Raises:
            RuntimeError: if the toml package is not available
            FileNotFoundError: if the toml could not be located

        """
        super().__attrs_post_init__()

        # Note: toml is an optional dependency required only when using the `doit_tasks` in development
        if toml is None:
            raise RuntimeError(_DOIT_TASK_IMPORT_ERROR)

        try:
            poetry_config = toml.load(self.path_toml)['tool']['poetry']
        except FileNotFoundError:
            raise FileNotFoundError(f'Check that "{self.path_project}" is correct. Could not find: {self.path_toml}')

        self.pkg_name = poetry_config['name']
        self.pkg_version = poetry_config['version']

        if '-' in self.pkg_name:
            warnings.warn(f'Replace dashes in name with underscores ({self.pkg_name}) in {self.path_toml}')


@attr.s(auto_attribs=True, kw_only=True)
class LintConfig(_PathAttrBase):  # noqa: H601
    """Lint Config."""

    path_flake8: Path = Path('.flake8')
    """Path to the flake8 configuration file."""

    paths: List[Path] = []
    """List of file and directory Paths to lint."""

    paths_excluded: List[Path] = _DEF_EXCLUDE
    """List of excluded relative Paths."""


@attr.s(auto_attribs=True, kw_only=True)
class TestingConfig(_PathAttrBase):  # noqa: H601
    """Test Config."""

    pythons: List[str] = ['3.7', '3.9']
    """Python versions to test against. Default is `['3.6', '3.9']`."""

    path_out: Path = Path('releases/tests')
    """Path to the report output directory. Default is `releases/tests`."""

    path_tests: Path = Path('tests')
    """Path to the tests directory. Default is `tests`."""

    def __attrs_post_init__(self) -> None:
        """Finish initializing class attributes."""
        super().__attrs_post_init__()
        self.path_out.mkdir(exist_ok=True, parents=True)
        # Configure the paths to the report HTML and coverage HTML files
        self.path_report_index = self.path_out / 'test_report.html'
        self.path_coverage_index = self.path_out / 'cov_html/index.html'


@attr.s(auto_attribs=True, kw_only=True)
class DocConfig(_PathAttrBase):  # noqa: H601
    """Documentation Config."""

    path_out: Path = Path('releases/site')
    """Path to the documentation output directory."""

    paths_excluded: List[Path] = _DEF_EXCLUDE
    """List of excluded relative Paths."""

    def __attrs_post_init__(self) -> None:
        """Finish initializing class attributes."""
        super().__attrs_post_init__()
        self.path_out.mkdir(exist_ok=True, parents=True)


@attr.s(auto_attribs=True, kw_only=True)
class DoItGlobals:
    """Global Variables for doit."""

    calcipy_dir: Path = Path(__file__).resolve().parents[1]
    """The calcipy directory (likely within `.venv`)."""

    meta: PackageMeta = attr.ib(init=False)
    """Package Meta-Information."""

    lint: LintConfig = attr.ib(init=False)
    """Lint Config."""

    test: TestingConfig = attr.ib(init=False)
    """Test Config."""

    doc: DocConfig = attr.ib(init=False)
    """Documentation Config."""

    @log_fun
    def set_paths(
        self, *, path_project: Optional[Path] = None,
        doc_dir: Optional[Path] = None,
    ) -> None:
        """Set data members based on working directory.

        Args:
            path_project: optional source directory Path. Defaults to the `pkg_name`
            doc_dir: optional destination directory for project documentation. Defaults to './output'

        """
        logger.info(f'Setting DIG path: {path_project}', path_project=path_project, cwd=Path.cwd(), doc_dir=doc_dir)
        path_project = Path.cwd() if path_project is None else path_project
        self.meta = PackageMeta(path_project=path_project)
        meta_kwargs = {'path_project': self.meta.path_project}

        self.lint = LintConfig(**meta_kwargs)
        self.lint.paths.append(self.meta.path_project / self.meta.pkg_name)

        self.test = TestingConfig(**meta_kwargs)
        self.doc = DocConfig(**meta_kwargs)

        logger.info(self)


DIG = DoItGlobals()
"""Global doit Globals class used to manage global variables."""

DIG.set_paths(path_project=Path.cwd().resolve())
