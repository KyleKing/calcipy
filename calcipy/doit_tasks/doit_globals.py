"""Global Variables for doit."""

import inspect
import re
import warnings
from functools import partial
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Pattern, Set, Tuple, Union

import attr
import yaml
from beartype import beartype
from doit.action import BaseAction
from doit.task import Task
from loguru import logger

from ..log_helpers import log_fun
from .file_search import find_project_files, find_project_files_by_suffix

try:
    import toml
except ImportError:  # pragma: no cover
    toml = None  # type: ignore[assignment]

_DOIT_TASK_IMPORT_ERROR = 'User must install the optional calcipy extra "dev" to utilize "doit_tasks"'
"""Standard error message when an optional import is not available. Raise with RuntimeError."""

_DoitCallableArgs = Iterable[Union[str, float, int, Path, Dict[str, Any]]]
"""Type: legal types that can be passed to a Python callable for doit actions."""

DoitAction = Union[str, BaseAction, Tuple[Callable, _DoitCallableArgs]]  # type: ignore[type-arg]
"""Type: individual doit action."""

DoitTask = Union[Task, Dict[str, DoitAction]]
"""Type: full doit task."""


@beartype
def _member_filter(member: Any, instance_type: Any) -> bool:
    """Return True if the member matches the filters.

    Args:
        member: class data- or method-member
        instance_type: optional instance type

    Returns:
        bool: True if the member matches the applied filter

    """
    return (instance_type is None or isinstance(member, instance_type))


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

    path_toml: Path = Path('pyproject.toml')
    """Path to the poetry toml file."""

    ignore_patterns: List[str] = []
    """List of glob patterns to ignore from all analysis."""

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
        if toml is None:  # pragma: no cover
            raise RuntimeError(_DOIT_TASK_IMPORT_ERROR)

        try:
            poetry_config = toml.load(self.path_toml)['tool']['poetry']
        except FileNotFoundError:  # pragma: no cover
            raise FileNotFoundError(f'Check that "{self.path_project}" is correct. Could not find: {self.path_toml}')

        self.pkg_name = poetry_config['name']
        self.pkg_version = poetry_config['version']

        if '-' in self.pkg_name:  # pragma: no cover
            warnings.warn(f'Replace dashes in name with underscores ({self.pkg_name}) in {self.path_toml}')


@attr.s(auto_attribs=True, kw_only=True)
class LintConfig(_PathAttrBase):  # noqa: H601
    """Lint Config."""

    path_flake8: Path = Path('.flake8')
    """Path to the flake8 configuration file. Default is ".flake8" created by calcipy_template."""

    path_isort: Path = Path('.isort.cfg')
    """Path to the isort configuration file. Default is ".isort.cfg" created by calcipy_template."""

    ignore_errors: List[str] = [
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
    """List of additional excluded flake8 rules for the pre-commit check."""

    def __attrs_post_init__(self) -> None:
        """Finish initializing class attributes."""
        super().__attrs_post_init__()
        self.paths_py = find_project_files_by_suffix(self.path_project, DG.meta.ignore_patterns).get('py', [])

    def __shorted_path_list(self) -> Set[str]:  # pragma: no cover
        """Shorten the list of `paths` using the project directory.

        > Not currently used, but could be useful

        Returns:
            Set[str]: set of most common top-level directories relative to the project dir

        """
        return {pth.parent.relative_to(self.project_dir).as_posix() for pth in self.paths}  # type: ignore[attr-defined]


@attr.s(auto_attribs=True, kw_only=True)
class TestingConfig(_PathAttrBase):  # noqa: H601
    """Test Config."""

    pythons: List[str] = ['3.8', '3.9']
    """Python versions to test against. Default is `['3.8', '3.9']`."""

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
        self.path_mypy_index = self.path_out / 'mypy_html/index.html'


@attr.s(auto_attribs=True, kw_only=True)
class CodeTagConfig(_PathAttrBase):  # noqa: H601
    """Code Tag Config."""

    doc_dir: Path = Path('docs')
    """Path to the source documentation directory."""

    _code_tag_summary_filename: str = 'CODE_TAG_SUMMARY.md'
    """Name of the code tag summary file."""

    tags: List[str] = [
        'FIXME', 'TODO', 'PLANNED', 'HACK', 'REVIEW', 'TBD', 'DEBUG', 'FYI', 'NOTE',  # noqa: T100,T101,T103
    ]
    """List of ordered tag names to match."""

    re_raw: str = r'((\s|\()(?P<tag>{tag})(:[^\r\n]))(?P<text>.+)'
    """string regular expression that contains `{tag}`."""

    def __attrs_post_init__(self) -> None:
        """Finish initializing class attributes."""
        super().__attrs_post_init__()
        # Configure full path to the code tag summary file
        self.path_code_tag_summary = self.doc_dir / self._code_tag_summary_filename
        self.paths = find_project_files(self.path_project, DG.meta.ignore_patterns)

    def compile_issue_regex(self) -> Pattern[str]:
        """Compile the regex for the specified raw regular expression string and tags.

        Returns:
            Pattern[str]: compiled regular expression to match all of the specified tags

        """
        return re.compile(self.re_raw.format(tag='|'.join(self.tags)))


@attr.s(auto_attribs=True, kw_only=True)
class DocConfig(_PathAttrBase):  # noqa: H601
    """Documentation Config."""

    doc_dir: Path = Path('docs')
    """Path to the source documentation directory."""

    path_out: Path = Path('releases/site')
    """Path to the documentation output directory."""

    startswith_action_lookup: Dict[str, Callable[[str, Path], str]] = {}
    """Lookup dictionary for autoformatted sections of the project's markdown files."""

    def __attrs_post_init__(self) -> None:
        """Finish initializing class attributes."""
        super().__attrs_post_init__()
        self.path_out.mkdir(exist_ok=True, parents=True)
        self.paths_md = find_project_files_by_suffix(self.path_project, DG.meta.ignore_patterns).get('md', [])


@attr.s(auto_attribs=True, kw_only=True)
class DoitGlobals:
    """Global Variables for doit."""

    calcipy_dir: Path = Path(__file__).resolve().parents[1]
    """The calcipy directory (likely within `.venv`)."""

    meta: PackageMeta = attr.ib(init=False)
    """Package Meta-Information."""

    lint: LintConfig = attr.ib(init=False)
    """Lint Config."""

    test: TestingConfig = attr.ib(init=False)
    """Test Config."""

    ct: CodeTagConfig = attr.ib(init=False)
    """Documentation Config."""

    doc: DocConfig = attr.ib(init=False)
    """Documentation Config."""

    @log_fun
    def set_paths(
        self, *, path_project: Optional[Path] = None,
    ) -> None:
        """Set data members based on working directory.

        Args:
            path_project: optional source directory Path. Defaults to the `pkg_name`

        """
        logger.info(f'Setting DG path: {path_project}', path_project=path_project, cwd=Path.cwd())
        path_project = Path.cwd() if path_project is None else path_project
        self.meta = PackageMeta(path_project=path_project)
        meta_kwargs = {'path_project': self.meta.path_project}

        # Parse the Copier file for configuration information
        path_copier = self.meta.path_project / '.copier-answers.yml'
        try:
            copier_ans = yaml.safe_load(path_copier.read_text())
            doc_dir = self.meta.path_project / copier_ans['doc_dir']
        except (FileNotFoundError, KeyError) as err:  # pragma: no cover
            logger.warning(f'Unexpected error reading the copier file: {err}')
            doc_dir = self.meta.path_project / 'docs'
        doc_dir.mkdir(exist_ok=True, parents=True)

        # Read the optional toml configuration
        # > Note: could allow LintConfig/.../DocConfig kwargs to be set in toml, but may be difficult to maintain
        path_toml = self.meta.path_project / 'pyproject.toml'
        toml_config = toml.load(path_toml).get('tool', {}).get('calcipy', {})
        self.meta.ignore_patterns = toml_config.get('ignore_patterns', [])

        self.lint = LintConfig(**meta_kwargs)  # type: ignore[arg-type]
        self.test = TestingConfig(**meta_kwargs)  # type: ignore[arg-type]
        self.ct = CodeTagConfig(**meta_kwargs, doc_dir=doc_dir)  # type: ignore[arg-type]
        self.doc = DocConfig(**meta_kwargs, doc_dir=doc_dir)  # type: ignore[arg-type]


DG = DoitGlobals()
"""Global doit Globals class used to manage global variables."""

DG.set_paths(path_project=Path.cwd().resolve())
