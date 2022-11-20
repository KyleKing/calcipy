# mypy: disable-error-code="misc"
# ^ ignores assignments to ClassVar
"""Global Variables for doit."""

import inspect
import re
import warnings
from functools import partial
from pathlib import Path
from typing import ClassVar
from uuid import uuid4

import doit
from beartype import beartype
from beartype.typing import Any, Callable, Dict, Iterable, List, Optional, Pattern, Set, Tuple, Union
from doit.action import BaseAction
from doit.task import Task
from loguru import logger
from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass

from ..code_tag_collector import CODE_TAG_RE, COMMON_CODE_TAGS
from ..file_helpers import _MKDOCS_CONFIG_NAME, _read_yaml_file, get_doc_dir
from ..file_search import find_project_files, find_project_files_by_suffix
from ..log_helpers import log_fun

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef]

_DOIT_TASK_IMPORT_ERROR = 'User must install the optional calcipy extra "dev" to utilize "doit_tasks"'
"""Standard error message when an optional import is not available. Raise with RuntimeError."""

_DoitCallableArgs = Iterable[Union[str, float, int, Path, Dict[str, Any]]]
"""Type: legal types that can be passed to a Python callable for doit actions."""

DoitAction = Union[str, BaseAction, Tuple[Callable, _DoitCallableArgs]]  # type: ignore[type-arg]
"""Type: individual doit action."""

# TODO: Better differentiate Task vs. Dict when typing and a dictionary is expected
DoitTask = Union[Task, Dict[str, DoitAction]]
"""Type: full doit task."""


@beartype
def _make_full_path(raw: Union[Path, str], *, path_base: Path) -> Path:
    """Return a full path by determining if the source path is an absolute path. If not combines with base path.

    Args:
        raw: (string or Path) relative or absolute path
        path_base: base directory to use if the raw path is not absolute

    Returns:
        Path: absolute path

    """
    return Path(raw) if Path(raw).is_absolute() else path_base / raw


@beartype
def _member_filter(member: Any, instance_type: Any) -> bool:
    """Return True if the member matches the filters.

    Args:
        member: class data- or method-member
        instance_type: optional instance type

    Returns:
        bool: True if the member matches the applied filter

    """
    return instance_type is None or isinstance(member, instance_type)


@dataclass
class _PathAttrBase:

    path_project: Path
    """Path to the package directory."""

    def __post_init__(self) -> None:
        """Initialize full paths with the package base directory if necessary.

        Raises:
            RuntimeError: if any paths are None

        """
        self._resolve_class_paths(self.path_project)

    @beartype
    def _get_members(self, prefix: Optional[str], **kwargs: Any) -> List[Tuple[str, Any]]:
        """Return the members that match the parameters.

        Example to return all methods that start with `do_`: `self._get_members(instance_type=Callable, prefix='do_')`

        Args:
            prefix: optional string prefix to check starts with
            **kwargs: keyword arguments passed to `_member_filter`

        Returns:
            List[Tuple[str, Any]]: filtered members from the class

        """
        members = inspect.getmembers(self, predicate=partial(_member_filter, **kwargs))
        return [
            (name, member) for (name, member) in members
            if not prefix or name.startswith(prefix)
        ]

    @beartype
    def _resolve_class_paths(self, base_path: Path) -> None:
        """Resolve all partial paths with the specified base path.

        WARN: will mutate the class attribute

        Args:
            base_path: base path to apply to all found relative paths

        """
        for name, path_raw in self._get_members(instance_type=type(Path()), prefix=None):
            if not path_raw.is_absolute():
                setattr(self, name, base_path / path_raw)
                logger.debug(f'Mutated: self.{name}={path_raw} (now: {getattr(self, name)})')


@dataclass
class PackageMeta(_PathAttrBase):
    """Package Meta-Information."""

    ignore_patterns: List[str] = Field(default_factory=list)
    """List of glob patterns to ignore from all analysis."""

    paths: ClassVar[List[Path]]
    """Paths to all tracked files that were not ignored with specified patterns `find_project_files`."""

    path_toml: ClassVar[Path]
    """Path to the poetry toml file."""

    pkg_name: ClassVar[str]
    """Package string name."""

    pkg_version: ClassVar[str]
    """Package version."""

    min_pyhon: ClassVar[Tuple[str]]
    """Minimum Python version from pyproject.toml file."""

    paths_by_suffix: ClassVar[Dict[str, List[Path]]]
    """Paths to all tracked files that were not ignored with specified patterns `find_project_files_by_suffix`."""

    def __post_init__(self) -> None:
        """Finish initializing class attributes.

        Raises:
            RuntimeError: if the toml package is not available
            FileNotFoundError: if the toml could not be located

        """
        super().__post_init__()

        self.path_toml = self.path_project / 'pyproject.toml'
        if not self.path_toml.is_file():
            raise RuntimeError(f'Check "path_project". Could not find: "{self.path_toml}"')

        poetry_config = tomllib.loads(self.path_toml.read_text())['tool']['poetry']
        self.pkg_name = poetry_config['name']
        self.pkg_version = poetry_config['version']
        py_constraint = poetry_config['dependencies']['python']
        self.min_python = py_constraint.split(',')[0].lstrip('^>=').split('.')
        if len(self.min_python) != 3 and self.min_python[0] != '3':
            raise ValueError(f'Could not parse a valid minimum Python 3 version from {py_constraint}')

        if '-' in self.pkg_name:  # pragma: no cover
            warnings.warn(f'Replace dashes in name with underscores ({self.pkg_name}) in {self.path_toml}')

        self.paths = find_project_files(self.path_project, self.ignore_patterns)
        self.paths_by_suffix = find_project_files_by_suffix(self.path_project, self.ignore_patterns)

    @beartype
    def _shorten_path_lists(self) -> Set[Path]:
        """Shorten the list of directories common to the specified paths.

        > FYI: Not currently needed, but could be useful

        Returns:
            Set[Path]: set of unique paths relative to project

        """
        return {
            pth.parent.relative_to(self.path_project)
            for pth in self.paths
        }


# FIXME: Merge with .flake8 configuration...
_DEF_IGNORE_LIST = [
    'AAA01',  # AAA01 / act block in pytest
    'C901',  # C901 / complexity from "max-complexity = 10"
    'D417',  # D417 / missing arg descriptors
    'DAR101', 'DAR201', 'DAR401',  # https://pypi.org/project/darglint/ (Scroll to error codes)
    'DUO106',  # DUO106 / insecure use of os
    'E800',  # E800 / Commented out code
    'G001',  # G001 / logging format for un-indexed parameters
    'H601',  # H601 / class with low cohesion
    'P101', 'P103',  # P101,P103 / format string
    'PD013',
    'S101',  # S101 / assert
    'S605', 'S607',  # S605,S607 / os.popen(...)
    'T100', 'T101', 'T103',  # T100,T101,T103 / fixme and todo comments
]
"""Default list of excluded flake8 rules for the pre-commit check (additional to .flake8)."""


@dataclass
class LintConfig(_PathAttrBase):
    """Lint Config."""

    paths_py: List[Path]
    """Paths to the Python files used when linting. Created with `find_project_files_by_suffix`."""

    path_flake8: Path = Field(default=Path('.flake8'))
    """Relative path to the flake8 configuration file. Default is ".flake8" created by calcipy_template."""

    path_isort: Path = Field(default=Path('pyproject.toml'))
    """Relative path to the isort configuration file. Default is "pyproject.toml" created by calcipy_template."""

    ignore_errors: List[str] = Field(default_factory=lambda: _DEF_IGNORE_LIST)
    """List of additional excluded flake8 rules for the pre-commit check."""

    def __post_init__(self) -> None:
        """Finish initializing class attributes."""
        super().__post_init__()
        self.path_flake8 = _make_full_path(self.path_flake8, path_base=self.path_project)
        self.path_isort = _make_full_path(self.path_isort, path_base=self.path_project)


@dataclass
class TestingConfig(_PathAttrBase):  # pylint: disable=too-many-instance-attributes
    """Test Config."""

    pythons: List[str] = Field(default_factory=lambda: ['3.8', '3.9'])
    """Python versions to test against. Default is `['3.8', '3.9']`.

    NOTE: Selecting a Python lower that calcipy's minimum may cause unexpected failures

    PLANNED: Consider adding a check to validate that the minimum Python is above calcipy's minimum

    """

    path_out: Path = Field(default=Path('releases/tests'))
    """Relative path to the report output directory. Default is `releases/tests`."""

    path_tests: Path = Field(default=Path('tests'))
    """Relative path to the tests directory. Default is `tests`."""

    min_cov: int = Field(default=80)
    """Configurable minimum percent coverage."""

    args_pytest: str = Field(default='--exitfirst --showlocals --failed-first --new-first --verbose')
    """Default arguments to Pytest"""

    path_test_report: ClassVar[Path]
    """Path to the self-contained test HTML report."""

    path_coverage_index: ClassVar[Path]
    """Path to the coverage HTML index file within the report directory."""

    path_mypy_index: ClassVar[Path]
    """Path to the mypy HTML index file within the report directory."""

    def __post_init__(self) -> None:
        """Finish initializing class attributes."""
        super().__post_init__()
        self.path_out = _make_full_path(self.path_out, path_base=self.path_project)
        self.path_tests = _make_full_path(self.path_tests, path_base=self.path_project)
        self.path_out.mkdir(exist_ok=True, parents=True)
        # Configure the paths to the report HTML and coverage HTML files
        self.path_test_report = self.path_out / 'test_report.html'
        self.path_coverage_index = self.path_out / 'cov_html/index.html'
        self.path_mypy_index = self.path_out / 'mypy_html/index.html'


@dataclass
class CodeTagConfig(_PathAttrBase):
    """Code Tag Config."""

    doc_sub_dir: Path = Field(default=Path('docs/docs'))
    """Relative path to the source documentation directory."""

    code_tag_summary_filename: str = Field(default='CODE_TAG_SUMMARY.md')
    """Name of the code tag summary file."""

    tags: List[str] = Field(default_factory=lambda: COMMON_CODE_TAGS)
    """List of ordered tag names to match."""

    re_raw: str = Field(default=CODE_TAG_RE)
    """string regular expression that contains `{tag}`."""

    path_code_tag_summary: ClassVar[Path]
    """Path to the code tag summary file. Uses `code_tag_summary_filename`."""

    def __post_init__(self) -> None:
        """Finish initializing class attributes."""
        super().__post_init__()
        # Configure full path to the code tag summary file
        self.path_code_tag_summary = (self.path_project / self.doc_sub_dir / self.code_tag_summary_filename)

    @beartype
    def compile_issue_regex(self) -> Pattern[str]:
        """Compile the regex for the specified raw regular expression string and tags.

        Returns:
            Pattern[str]: compiled regular expression to match all of the specified tags

        """
        return re.compile(self.re_raw.format(tag='|'.join(self.tags)))


@dataclass
class DocConfig(_PathAttrBase):
    """Documentation Config."""

    paths_md: List[Path]
    """Paths to Markdown files used when documenting. Created with `find_project_files_by_suffix`."""

    doc_sub_dir: Path = Field(default=Path('docs/docs'))
    """Relative path to the source documentation directory."""

    auto_doc_path: ClassVar[Path]
    """Auto-calculated based on `self.doc_sub_dir`."""

    handler_lookup: Optional[Dict[str, Callable[[str, Path], List[str]]]] = Field(default=None)
    """Lookup dictionary for autoformatted sections of the project's markdown files."""

    path_out: ClassVar[Path]
    """The documentation output directory. Specified in `mkdocs.yml`."""

    def __post_init__(self) -> None:
        """Finish initializing class attributes."""
        super().__post_init__()
        mkdocs_config = _read_yaml_file(self.path_project / _MKDOCS_CONFIG_NAME)
        self.path_out = Path(mkdocs_config.get('site_dir', 'releases/site'))
        self.path_out = _make_full_path(self.path_out, path_base=self.path_project)
        self.path_out.mkdir(exist_ok=True, parents=True)
        self.auto_doc_path = self.doc_sub_dir.parent / 'modules'


class DoitGlobals(BaseModel):
    """Global Variables for doit."""

    meta: PackageMeta
    """Package Meta-Information."""

    lint: LintConfig
    """Lint Config."""

    test: TestingConfig
    """Test Config."""

    tags: CodeTagConfig
    """Documentation Config."""

    doc: DocConfig
    """Documentation Config."""

    calcipy_dir: Path = Field(default=Path(__file__).resolve().parents[1])
    """The calcipy directory (likely within `.venv`)."""


@beartype
def _set_meta(path_project: Path, calcipy_config: Dict[str, Any]) -> PackageMeta:
    """Initialize the meta submodules.

    Args:
        path_project: project base directory Path
        calcipy_config: custom calcipy configuration from toml file

    """
    ignore_patterns = calcipy_config.get('ignore_patterns', [])
    return PackageMeta(path_project=path_project, ignore_patterns=ignore_patterns)


@beartype
def _set_submodules(
    meta: PackageMeta, calcipy_config: Dict[str, Any],
) -> Dict[str, Union[LintConfig, TestingConfig, CodeTagConfig, DocConfig]]:
    """Initialize the rest of the submodules.

    Args:
        calcipy_config: custom calcipy configuration from toml file

    Raises:
        RuntimeError: if problems in formatting of the toml file

    """
    # Configure global options
    section_keys = ['lint', 'test', 'code_tag', 'doc']
    supported_keys = section_keys + ['ignore_patterns']
    if unexpected_keys := [
        key for key in calcipy_config if key not in supported_keys
    ]:
        raise RuntimeError(f'Found unexpected key(s) {unexpected_keys} (i.e. not in {supported_keys})')

    # Parse the Copier file for configuration information
    doc_sub_dir = get_doc_dir(meta.path_project) / 'docs'  # Note: subdirectory is important
    doc_sub_dir.mkdir(exist_ok=True, parents=True)

    # Configure submodules
    meta_kwargs = {'path_project': meta.path_project}
    lint_k, test_k, code_k, doc_k = (calcipy_config.get(key, {}) for key in section_keys)
    paths_py = meta.paths_by_suffix.get('py', [])
    paths_md = meta.paths_by_suffix.get('md', [])
    return {
        'lint': LintConfig(**meta_kwargs, paths_py=paths_py, **lint_k),  # type: ignore[arg-type]
        'test': TestingConfig(**meta_kwargs, **test_k),  # type: ignore[arg-type]
        'tags': CodeTagConfig(**meta_kwargs, doc_sub_dir=doc_sub_dir, **code_k),  # type: ignore[arg-type]
        'doc': DocConfig(**meta_kwargs, paths_md=paths_md, doc_sub_dir=doc_sub_dir, **doc_k),  # type: ignore[arg-type]
    }


@log_fun
def create_dg(*, path_project: Path) -> DoitGlobals:
    """Configure `DoitGlobals` based on project directory.

    Args:
        path_project: optional project base directory Path. Defaults to the current working directory

    """
    logger.info('Setting DG path: {path_project}', path_project=path_project)

    # Read the optional toml configuration
    # > Note: could allow LintConfig/.../DocConfig kwargs to be set in toml, but may be difficult to maintain
    data = (path_project / 'pyproject.toml').read_text()
    calcipy_config = tomllib.loads(data).get('tool', {}).get('calcipy', {})

    meta = _set_meta(path_project, calcipy_config)
    kwargs = _set_submodules(meta, calcipy_config)
    return DoitGlobals(meta=meta, **kwargs)  # type: ignore[arg-type]


class _DGContainer(BaseModel):
    """Manage state of DoitGlobals.

    Only used for unit testing.

    """

    key: str = Field(default='')
    data: Dict[str, DoitGlobals] = Field(default_factory=dict)

    @beartype
    def set_dg(self, dg: DoitGlobals) -> None:
        """Registers a DG instance.

        Args:
            dg: Global doit 'Globals' class for management of global variables

        """
        self.key = str(uuid4())
        self.data[self.key] = dg

    @beartype
    def get_dg(self) -> DoitGlobals:
        """Retrieves the registered DG instance.

        Args:
            dg: Global doit 'Globals' class for management of global variables

        """
        return self.data[self.key]


_DG_CONTAINER = _DGContainer()
"""Single instance."""

set_dg = _DG_CONTAINER.set_dg
get_dg = _DG_CONTAINER.get_dg
"""Alias for exported function."""


@beartype
def init_dg() -> None:
    """Initialize the global DG instance."""
    work_dir = doit.get_initial_workdir()
    path_project = (Path(work_dir) if work_dir else Path.cwd()).resolve()
    dg = create_dg(path_project=path_project)
    set_dg(dg)


# Eagerly initialize at least one global DG instance
init_dg()
