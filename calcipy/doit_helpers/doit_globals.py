"""Global Variables for DoIt."""

import inspect
import warnings
from functools import partial
from pathlib import Path
from typing import Any, Callable, Dict, List, NewType, Optional, Sequence, Tuple, Union

import attr
import toml
from loguru import logger

from ..log_helpers import log_fun

# ----------------------------------------------------------------------------------------------------------------------
# Global Variables

DoItTask = NewType('DoItTask', Dict[str, Union[str, Tuple[Callable, Sequence]]])  # noqa: ECE001
"""DoIt task type for annotations."""


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
        logger.debug(f'self.{name}={path_raw} ({path_raw.is_absolute()})')
        if not path_raw.is_absolute():
            setattr(cls, name, base_path / path_raw)
            logger.info(f'Mutated: self.{name}={path_raw} (now: {getattr(cls, name)})')


_DEF_EXCLUDE = [*map(Path, ['__init__.py'])]
"""Default list of excluded filenames."""


@attr.s(auto_attribs=True, kw_only=True)
class _PathAttrBase:  # noqa: H601

    path_source: Path
    """Path to the package directory."""

    def __attrs_post_init__(self) -> None:
        """Initialize full paths with the package base directory if necessary.

        Raises:
            RuntimeError: if any paths are None

        """
        if self.path_source is None:
            raise RuntimeError('Missing keyword argument "path_source"')
        _resolve_class_paths(self, self.path_source)
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
            FileNotFoundError: if the toml could not be located

        """
        super().__attrs_post_init__()
        try:
            poetry_config = toml.load(self.path_toml)['tool']['poetry']
        except FileNotFoundError:
            raise FileNotFoundError(f'Check that "{self.path_source}" is correct. Could not find: {self.path_toml}')

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

    path_out: Path
    """Path to the report output directory."""

    path_tests: Path = Path('tests')
    """Path to the tests directory."""

    path_report_index: Path = attr.ib(init=False)
    """Path to the report HTML file."""

    path_coverage_index: Path = attr.ib(init=False)
    """Path to the coverage HTML file."""

    def __attrs_post_init__(self) -> None:
        """Finish initializing class attributes."""
        super().__attrs_post_init__()
        self.path_report_index = self.path_out / 'test_report.html'
        self.path_coverage_index = self.path_out / 'cov_html/index.html'


@attr.s(auto_attribs=True, kw_only=True)
class DocConfig(_PathAttrBase):  # noqa: H601
    """Documentation Config."""

    path_out: Path = Path('docs')
    """Path to the documentation output directory."""

    path_changelog: Path = Path(__file__).resolve().parents[1] / '.gitchangelog.rc'
    """Path to the changelog configuration file."""

    paths_excluded: List[Path] = _DEF_EXCLUDE
    """List of excluded relative Paths."""


@attr.s(auto_attribs=True, kw_only=True)
class DoItGlobals:
    """Global Variables for DoIt."""

    calcipy_dir: Path = Path(__file__).parents[1]
    """The calcipy directory (likely within `.venv`)."""

    meta: PackageMeta = attr.ib(init=False)  # PLANNED: Check if Optional[PackageMeta] is necessary
    """Package Meta-Information."""

    lint: LintConfig = attr.ib(init=False)
    """Lint Config."""

    test: TestingConfig = attr.ib(init=False)
    """Test Config."""

    doc: DocConfig = attr.ib(init=False)
    """Documentation Config."""

    @log_fun
    def set_paths(self, *, path_source: Optional[Path] = None,
                  doc_dir: Optional[Path] = None) -> None:
        """Set data members based on working directory.

        Args:
            path_source: optional source directory Path. Defaults to the `pkg_name`
            doc_dir: optional destination directory for project documentation. Defaults to './output'

        """
        logger.info(f'Setting DIG paths for {path_source}', path_source=path_source, cwd=Path.cwd(), doc_dir=doc_dir)
        path_source = Path.cwd() if path_source is None else path_source
        self.meta = PackageMeta(path_source=path_source)
        meta_kwargs = {'path_source': self.meta.path_source}

        self.lint = LintConfig(**meta_kwargs)
        self.lint.paths.append(self.meta.path_source / self.meta.pkg_name)

        self.test = TestingConfig(path_out=Path(), **meta_kwargs)

        doc_dir = self.meta.path_source / 'docs' if doc_dir is None else doc_dir
        self.doc = DocConfig(path_out=doc_dir, **meta_kwargs)

        logger.info(self)


DIG = DoItGlobals()
"""Global DoIt Globals class used to manage global variables."""
