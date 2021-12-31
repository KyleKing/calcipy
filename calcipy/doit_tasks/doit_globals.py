"""Global Variables for doit."""

import inspect
import re
import warnings
from functools import partial
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Pattern, Set, Tuple, Union

import attr
import doit
import tomli
from attrs_strict import type_validator
from beartype import beartype
from doit.action import BaseAction
from doit.task import Task
from loguru import logger

from ..code_tag_collector import CODE_TAG_RE, COMMON_CODE_TAGS
from ..file_helpers import _MKDOCS_CONFIG_NAME, _read_yaml_file, get_doc_dir
from ..file_search import find_project_files, find_project_files_by_suffix
from ..log_helpers import log_fun

_DOIT_TASK_IMPORT_ERROR = 'User must install the optional calcipy extra "dev" to utilize "doit_tasks"'
"""Standard error message when an optional import is not available. Raise with RuntimeError."""

_DoitCallableArgs = Iterable[Union[str, float, int, Path, Dict[str, Any]]]
"""Type: legal types that can be passed to a Python callable for doit actions."""

DoitAction = Union[str, BaseAction, Tuple[Callable, _DoitCallableArgs]]  # type: ignore[type-arg]
"""Type: individual doit action."""

DoitTask = Union[Task, Dict[str, DoitAction]]
"""Type: full doit task."""


@beartype
def _make_full_path(raw: Union[Path, str], path_base: Path) -> Path:
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


@attr.s(auto_attribs=True, kw_only=True)
class _PathAttrBase:  # noqa: H601

    path_project: Path = attr.ib(validator=type_validator())
    """Path to the package directory."""

    def __attrs_post_init__(self) -> None:
        """Initialize full paths with the package base directory if necessary.

        Raises:
            RuntimeError: if any paths are None

        """
        if self.path_project is None:
            raise RuntimeError('Missing keyword argument "path_project"')  # pragma: no cover
        self._resolve_class_paths(self.path_project)
        self._verify_initialized_paths()

    def _get_members(self, prefix: Optional[str], **kwargs: Any) -> List[Tuple[str, Callable[[Any], Any]]]:
        """Return the members that match the parameters.

        Example to return all methods that start with `do_`: `self._get_members(instance_type=Callable, prefix='do_')`

        Args:
            prefix: optional string prefix to check starts with
            kwargs: keyword arguments passed to `_member_filter`

        Returns:
            List[Tuple[str, Callable]]: filtered members from the class

        """
        members = inspect.getmembers(self, predicate=partial(_member_filter, **kwargs))
        if prefix:
            members = [(name, member) for (name, member) in members if name.startswith(prefix)]
        return members  # noqa: R504

    def _resolve_class_paths(self, base_path: Path) -> None:
        """Resolve all partial paths with the specified base path.

        WARN: will mutate the class attribute

        Args:
            base_path: base path to apply to all found relative paths

        """
        for name, path_raw in self._get_members(instance_type=type(Path()), prefix=None):
            if not path_raw.is_absolute():  # type: ignore[attr-defined]
                setattr(self, name, base_path / path_raw)  # type: ignore[operator]
                logger.debug(f'Mutated: self.{name}={path_raw} (now: {getattr(self, name)})')

    def _verify_initialized_paths(self) -> None:
        """Verify that all paths are not None.

        WARN: will not raise on error the class attribute

        Raises:
            RuntimeError: if any paths are None

        """
        missing = [name for name, _m in self._get_members(instance_type=type(None), prefix='path_')]
        if missing:
            kwargs = ', '.join(missing)
            raise RuntimeError(f'Missing keyword arguments for: {kwargs}')


@attr.s(auto_attribs=True, kw_only=True)
class PackageMeta(_PathAttrBase):  # noqa: H601
    """Package Meta-Information."""

    path_toml: Path = attr.ib(validator=type_validator(), default=Path('pyproject.toml'))
    """Relative path to the poetry toml file."""

    ignore_patterns: List[str] = attr.ib(validator=type_validator(), factory=list)
    """List of glob patterns to ignore from all analysis."""

    paths: List[Path] = attr.ib(validator=type_validator(), init=False)
    """Paths to all tracked files that were not ignored with specified patterns `find_project_files`."""

    paths_by_suffix: Dict[str, List[Path]] = attr.ib(validator=type_validator(), init=False)
    """Paths to all tracked files that were not ignored with specified patterns `find_project_files_by_suffix`."""

    pkg_name: str = attr.ib(validator=type_validator(), init=False)
    """Package string name."""

    pkg_version: str = attr.ib(validator=type_validator(), init=False)
    """Package version."""

    def __attrs_post_init__(self) -> None:
        """Finish initializing class attributes.

        Raises:
            RuntimeError: if the toml package is not available
            FileNotFoundError: if the toml could not be located

        """
        super().__attrs_post_init__()

        # Note: toml is an optional dependency required only when using the `doit_tasks` in development
        if tomli is None:  # pragma: no cover
            raise RuntimeError(_DOIT_TASK_IMPORT_ERROR)

        if not self.path_toml.is_file():
            raise RuntimeError(f'Check "{self.path_project}". Could not find: "{self.path_toml}"')

        poetry_config = tomli.loads(self.path_toml.read_text())['tool']['poetry']
        self.pkg_name = poetry_config['name']
        self.pkg_version = poetry_config['version']

        if '-' in self.pkg_name:  # pragma: no cover
            warnings.warn(f'Replace dashes in name with underscores ({self.pkg_name}) in {self.path_toml}')

        self.paths = find_project_files(self.path_project, self.ignore_patterns)
        self.paths_by_suffix = find_project_files_by_suffix(self.path_project, self.ignore_patterns)

    def __shorted_path_list(self) -> Set[str]:  # pragma: no cover
        """Shorten the list of directories common to the specified paths.

        > Not currently needed, but could be useful

        Returns:
            Set[str]: set of most common top-level directories relative to the project dir

        """
        return {
            pth.parent.relative_to(self.path_project).as_posix()
            for pth in self.paths
        }  # type: ignore[attr-defined]


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


@attr.s(auto_attribs=True, kw_only=True)
class LintConfig(_PathAttrBase):  # noqa: H601
    """Lint Config."""

    path_flake8: Union[Path, str] = attr.ib(validator=type_validator(), default=Path('.flake8'))
    """Relative path to the flake8 configuration file. Default is ".flake8" created by calcipy_template."""

    path_isort: Union[Path, str] = attr.ib(validator=type_validator(), default=Path('pyproject.toml'))
    """Relative path to the isort configuration file. Default is "pyproject.toml" created by calcipy_template."""

    ignore_errors: List[str] = attr.ib(validator=type_validator(), factory=lambda: _DEF_IGNORE_LIST)
    """List of additional excluded flake8 rules for the pre-commit check."""

    paths_py: List[Path] = attr.ib(validator=type_validator(), init=False)
    """Paths to the Python files used when linting. Created with `find_project_files_by_suffix`."""

    def __attrs_post_init__(self) -> None:
        """Finish initializing class attributes."""
        super().__attrs_post_init__()
        self.path_flake8 = _make_full_path(self.path_flake8, self.path_project)
        self.path_isort = _make_full_path(self.path_isort, self.path_project)
        self.paths_py = DG.meta.paths_by_suffix.get('py', [])


@attr.s(auto_attribs=True, kw_only=True)
class TestingConfig(_PathAttrBase):  # noqa: H601  # pylint: disable=too-many-instance-attributes
    """Test Config."""

    pythons: List[str] = attr.ib(validator=type_validator(), factory=lambda: ['3.8', '3.9'])
    """Python versions to test against. Default is `['3.8', '3.9']`."""

    path_out: Union[Path, str] = attr.ib(validator=type_validator(), default=Path('releases/tests'))
    """Relative path to the report output directory. Default is `releases/tests`."""

    path_tests: Union[Path, str] = attr.ib(validator=type_validator(), default=Path('tests'))
    """Relative path to the tests directory. Default is `tests`."""

    args_pytest: str = attr.ib(
        validator=type_validator(),
        default='--exitfirst --showlocals --failed-first --new-first --verbose --doctest-modules',
    )
    """Default arguments to Pytest. In short form, the defaults are `-x -l --ff --nf -vv`."""

    args_diff: str = attr.ib(validator=type_validator(), default='--fail-under=65 --compare-branch=origin/main')
    """Default arguments to diff-cover."""

    path_test_report: Path = attr.ib(validator=type_validator(), init=False)
    """Path to the self-contained test HTML report."""

    path_diff_test_report: Path = attr.ib(validator=type_validator(), init=False)
    """Path to the self-contained diff-test HTML report."""

    path_diff_lint_report: Path = attr.ib(validator=type_validator(), init=False)
    """Path to the self-contained diff-lint HTML report."""

    path_coverage_index: Path = attr.ib(validator=type_validator(), init=False)
    """Path to the coverage HTML index file within the report directory."""

    path_mypy_index: Path = attr.ib(validator=type_validator(), init=False)
    """Path to the mypy HTML index file within the report directory."""

    def __attrs_post_init__(self) -> None:
        """Finish initializing class attributes."""
        super().__attrs_post_init__()
        self.path_out = _make_full_path(self.path_out, self.path_project)
        self.path_tests = _make_full_path(self.path_tests, self.path_project)
        self.path_out.mkdir(exist_ok=True, parents=True)
        # Configure the paths to the report HTML and coverage HTML files
        self.path_test_report = self.path_out / 'test_report.html'
        self.path_diff_test_report = self.path_out / 'diff_test_report.html'
        self.path_diff_lint_report = self.path_out / 'diff_lint_report.html'
        self.path_coverage_index = self.path_out / 'cov_html/index.html'
        self.path_mypy_index = self.path_out / 'mypy_html/index.html'


@attr.s(auto_attribs=True, kw_only=True)
class CodeTagConfig(_PathAttrBase):  # noqa: H601
    """Code Tag Config."""

    doc_sub_dir: Path = attr.ib(validator=type_validator(), default=Path('docs/docs'))
    """Relative path to the source documentation directory."""

    code_tag_summary_filename: str = attr.ib(validator=type_validator(), default='CODE_TAG_SUMMARY.md')
    """Name of the code tag summary file."""

    tags: List[str] = attr.ib(validator=type_validator(), factory=lambda: COMMON_CODE_TAGS)
    """List of ordered tag names to match."""

    re_raw: str = attr.ib(validator=type_validator(), default=CODE_TAG_RE)
    """string regular expression that contains `{tag}`."""

    path_code_tag_summary: Path = attr.ib(validator=type_validator(), init=False)
    """Path to the code tag summary file. Uses `code_tag_summary_filename`."""

    def __attrs_post_init__(self) -> None:
        """Finish initializing class attributes."""
        super().__attrs_post_init__()
        # Configure full path to the code tag summary file
        self.path_code_tag_summary = self.path_project / self.doc_sub_dir / self.code_tag_summary_filename

    def compile_issue_regex(self) -> Pattern[str]:
        """Compile the regex for the specified raw regular expression string and tags.

        Returns:
            Pattern[str]: compiled regular expression to match all of the specified tags

        """
        return re.compile(self.re_raw.format(tag='|'.join(self.tags)))


@attr.s(auto_attribs=True, kw_only=True)
class DocConfig(_PathAttrBase):  # noqa: H601
    """Documentation Config."""

    doc_sub_dir: Path = attr.ib(validator=type_validator(), default=Path('docs/docs'))
    """Relative path to the source documentation directory."""

    auto_doc_path: Optional[Path] = attr.ib(validator=type_validator(), default=None)
    """Auto-calculated based on `self.doc_sub_dir`."""

    handler_lookup: Optional[Dict[str, Callable[[str, Path], str]]] = attr.ib(validator=type_validator(), default=None)
    """Lookup dictionary for autoformatted sections of the project's markdown files."""

    path_out: Path = attr.ib(validator=type_validator(), init=False)
    """The documentation output directory. Specified in `mkdocs.yml`."""

    paths_md: List[Path] = attr.ib(validator=type_validator(), init=False)
    """Paths to Markdown files used when documenting. Created with `find_project_files_by_suffix`."""

    def __attrs_post_init__(self) -> None:
        """Finish initializing class attributes."""
        super().__attrs_post_init__()
        mkdocs_config = _read_yaml_file(self.path_project / _MKDOCS_CONFIG_NAME)
        self.path_out = mkdocs_config.get('site_dir', 'releases/site')
        self.path_out = _make_full_path(self.path_out, self.path_project)
        self.path_out.mkdir(exist_ok=True, parents=True)
        self.paths_md = DG.meta.paths_by_suffix.get('md', [])
        self.auto_doc_path = self.doc_sub_dir.parent / 'modules'


@attr.s(auto_attribs=True, kw_only=True)
class DoitGlobals:  # noqa: H601  # pylint: disable=too-many-instance-attributes
    """Global Variables for doit."""

    calcipy_dir: Path = attr.ib(validator=type_validator(), init=False, default=Path(__file__).resolve().parents[1])
    """The calcipy directory (likely within `.venv`)."""

    meta: PackageMeta = attr.ib(validator=type_validator(), init=False)
    """Package Meta-Information."""

    lint: LintConfig = attr.ib(validator=type_validator(), init=False)
    """Lint Config."""

    test: TestingConfig = attr.ib(validator=type_validator(), init=False)
    """Test Config."""

    tags: CodeTagConfig = attr.ib(validator=type_validator(), init=False)
    """Documentation Config."""

    doc: DocConfig = attr.ib(validator=type_validator(), init=False)
    """Documentation Config."""

    _is_set: bool = attr.ib(validator=type_validator(), default=False)
    """Internal flag to check if already set."""

    @log_fun
    def set_paths(
        self, *, path_project: Optional[Path] = None,
    ) -> None:
        """Configure `DoitGlobals` based on project directory.

        Args:
            path_project: optional project base directory Path. Defaults to the current working directory

        Raises:
            RuntimeError: if `set_paths` is called twice. This can cause unexpected behavior, so if
                absolutely necessary, set `DG._is_set = False`, then try `DG.set_paths()`

        """
        if self._is_set:
            raise RuntimeError('DoitGlobals has already been configured and cannot be reconfigured')

        logger.info(f'Setting DG path: {path_project}', path_project=path_project, cwd=Path.cwd())
        path_project = path_project or Path.cwd()

        # Read the optional toml configuration
        # > Note: could allow LintConfig/.../DocConfig kwargs to be set in toml, but may be difficult to maintain
        data = (path_project / 'pyproject.toml').read_text()
        calcipy_config = tomli.loads(data).get('tool', {}).get('calcipy', {})

        self._set_meta(path_project, calcipy_config)
        self._set_submodules(calcipy_config)

        self._is_set = True

    def _set_meta(self, path_project: Path, calcipy_config: Dict[str, Any]) -> None:
        """Initialize the meta submodules.

        Args:
            path_project: project base directory Path
            calcipy_config: custom calcipy configuration from toml file

        """
        ignore_patterns = calcipy_config.get('ignore_patterns', [])
        self.meta = PackageMeta(path_project=path_project, ignore_patterns=ignore_patterns)

    def _set_submodules(self, calcipy_config: Dict[str, Any]) -> None:
        """Initialize the rest of the submodules.

        Args:
            calcipy_config: custom calcipy configuration from toml file

        Raises:
            RuntimeError: if problems in formatting of the toml file

        """
        # Configure global options
        section_keys = ['lint', 'test', 'code_tag', 'doc']
        supported_keys = section_keys + ['ignore_patterns']
        unexpected_keys = [key for key in calcipy_config if key not in supported_keys]
        if unexpected_keys:
            raise RuntimeError(f'Found unexpected key(s) {unexpected_keys} (i.e. not in {supported_keys})')

        # Parse the Copier file for configuration information
        doc_sub_dir = get_doc_dir(self.meta.path_project) / 'docs'  # Note: subdirectory is important
        doc_sub_dir.mkdir(exist_ok=True, parents=True)

        # Configure submodules
        meta_kwargs = {'path_project': self.meta.path_project}
        lint_k, test_k, code_k, doc_k = (calcipy_config.get(key, {}) for key in section_keys)
        self.lint = LintConfig(**meta_kwargs, **lint_k)  # type: ignore[arg-type]
        self.test = TestingConfig(**meta_kwargs, **test_k)  # type: ignore[arg-type]
        self.tags = CodeTagConfig(**meta_kwargs, doc_sub_dir=doc_sub_dir, **code_k)  # type: ignore[arg-type]
        self.doc = DocConfig(**meta_kwargs, doc_sub_dir=doc_sub_dir, **doc_k)  # type: ignore[arg-type]


DG = DoitGlobals()
"""Global doit Globals class used to manage global variables."""

_WORK_DIR = doit.get_initial_workdir()
"""Work directory identified by doit."""

DG.set_paths(path_project=(Path(_WORK_DIR) if _WORK_DIR else Path.cwd()).resolve())
