"""doit Documentation Utilities."""

import json
import re
import webbrowser
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Pattern

import pandas as pd
from beartype import beartype
from doit.tools import Interactive
from loguru import logger
from transitions import Machine

from ..file_helpers import _MKDOCS_CONFIG_NAME, _read_yaml_file, delete_dir, read_lines, trim_trailing_whitespace
from .base import debug_task, echo, open_in_browser, write_text
from .doit_globals import DG, DoitAction, DoitTask

# ----------------------------------------------------------------------------------------------------------------------
# Manage Changelog


@beartype
def _move_cl() -> None:
    """Move the `CHANGELOG.md` file to the document directory.

    Raises:
        FileNotFoundError: if the changelog was not found

    """
    path_cl = DG.meta.path_project / 'CHANGELOG.md'
    if not path_cl.is_file():
        raise FileNotFoundError(f'Could not locate the changelog at: {path_cl}')
    path_cl.replace(DG.doc.doc_sub_dir / path_cl.name)


@beartype
def _write_changelog() -> List[DoitAction]:
    """Write a Changelog file with the raw Git history.

    Resources:

    - https://keepachangelog.com/en/1.0.0/
    - https://www.conventionalcommits.org/en/v1.0.0/
    - https://writingfordevelopers.substack.com/p/how-to-write-a-commit-message
    - https://chris.beams.io/posts/git-commit/
    - https://semver.org/
    - https://calver.org/

    Returns:
        List[DoitAction]: doit actions

    """
    return [
        'poetry run cz changelog',
        (_move_cl, ()),
    ]


@beartype
def task_cl_write() -> DoitTask:
    """Auto-generate the changelog based on commit history and tags.

    Returns:
        DoitTask: doit task

    """
    return debug_task(_write_changelog())


@beartype
def task_cl_bump() -> DoitTask:
    """Bumps project version based on commits & settings in pyproject.toml.

    Returns:
        DoitTask: doit task

    """
    return debug_task([
        *_write_changelog(),
        Interactive('poetry run cz bump --annotated-tag'),
        'git push origin --tags --no-verify',
    ])


@beartype
def task_cl_bump_pre() -> DoitTask:
    """Bump with specified pre-release tag. Requires a parameter (`-p alpha`, `-p beta`, `-p rc`, etc.).

    Example: `doit run cl_bump_pre -p alpha` or `doit run cl_bump_pre -p rc`

    Returns:
        DoitTask: doit task

    """
    task = debug_task([
        *_write_changelog(),
        Interactive('poetry run cz bump --prerelease %(prerelease)s'),
        'git push origin --tags --no-verify',
    ])
    task['params'] = [{
        'name': 'prerelease', 'short': 'p', 'long': 'prerelease', 'default': '',
        'help': 'Specify prerelease version for bump (alpha, beta, rc)',
    }]
    return task


# ----------------------------------------------------------------------------------------------------------------------
# Manage README Updates


class _ReplacementMachine(Machine):  # type: ignore[misc] # noqa: H601
    """State machine to replace content with user-specified handlers.

    Uses `{cts}` and `{cte}` to demarcate sections (short for calcipy_template start|end)

    """

    def __init__(self) -> None:
        """Initialize the state machine."""
        self.state_user = 'user'
        self.state_auto = 'autoformatted'
        transitions = [
            {
                'trigger': 'start_auto',
                'source': self.state_user,
                'dest': self.state_auto,
            }, {
                'trigger': 'end',
                'source': self.state_auto,
                'dest': self.state_user,
            },
        ]
        super().__init__(
            states=[self.state_user, self.state_auto],
            initial=self.state_user,
            transitions=transitions,
        )

    def _parse_line(
        self, line: str, handler_lookup: Dict[str, Callable[[str, Path], str]],
        path_file: Optional[Path] = None,
    ) -> List[str]:
        """Parse lines and insert new_text based on provided handler_lookup.

        Args:
            line: single line
            handler_lookup: Lookup dictionary for autoformatted sections
            path_file: optional path to the file. Only useful for debugging

        Returns:
            List[str]: modified list of strings

        """
        lines: List[str] = []
        if '{cte}' in line and self.state == self.state_auto:  # end
            self.end()
        elif '{cts}' in line:  # start
            self.start_auto()
            matches = [text_match for text_match in handler_lookup if text_match in line]
            if len(matches) == 1:
                lines.extend(handler_lookup[matches[0]](line, path_file))
            else:
                logger.error('Could not parse: {line}', line=line)
                lines.append(line)
                self.end()
        elif self.state == self.state_user:
            lines.append(line)
        # else: discard the lines in the auto-section
        return lines

    def parse(
        self, lines: List[str], handler_lookup: Dict[str, Callable[[str, Path], str]],
        path_file: Optional[Path] = None,
    ) -> List[str]:
        """Parse lines and insert new_text based on provided handler_lookup.

        Args:
            lines: list of string from source file
            handler_lookup: Lookup dictionary for autoformatted sections
            path_file: optional path to the file. Only useful for debugging

        Returns:
            List[str]: modified list of strings

        """
        updated_lines = []
        for line in lines:
            updated_lines.extend(self._parse_line(line, handler_lookup, path_file))
        return updated_lines


_RE_VAR_COMMENT_HTML = re.compile(r'<!-- {cts} (?P<key>[^=]+)=(?P<value>[^;]+);')
"""Regex for extracting the vairable from an HTML code comment."""


@beartype
def _parse_var_comment(line: str, matcher: Pattern = _RE_VAR_COMMENT_HTML) -> Dict[str, str]:
    """Parse the variable from a matching comment.

    Args:
        line: string from source file
        matcher: regex pattern to match. Default is `_RE_VAR_COMMENT_HTML`

    Returns:
        Dict[str, str]: single key and value pair based on the parsed comment

    """
    match = matcher.match(line.strip())
    if match:
        matches = match.groupdict()
        return {matches['key']: matches['value']}
    return {}


@beartype
def _handle_source_file(line: str, path_file: Path) -> List[str]:
    """Replace commented sections in README with linked file contents.

    Args:
        line: first line of the section
        path_file: path to the file that contained the string

    Returns:
        List[str]: list of auto-formatted text

    """
    key, path_rel = [*_parse_var_comment(line).items()][0]
    path_base = DG.meta.path_project if path_rel.startswith('/') else path_file.resolve().parent
    path_source = path_base / path_rel.lstrip('/')
    language = path_source.suffix.lstrip('.')
    lines_source = [f'```{language}', *read_lines(path_source), '```']
    if not path_source.is_file():
        logger.warning(f'Could not locate: {path_source}')

    line_start = f'<!-- {{cts}} {key}={path_rel}; -->'
    line_end = '<!-- {cte} -->'
    return [line_start] + lines_source + [line_end]


@beartype
def _format_cov_table(coverage_data: Dict[str, Any]) -> List[str]:
    """Format code coverage data table as markdown.

    Args:
        coverage_data: dictionary created by `python -m coverage json`

    Returns:
        List[str]: list of string lines to insert

    """
    col_key_map = {
        'Statements': 'num_statements',
        'Missing': 'missing_lines',
        'Excluded': 'excluded_lines',
        'Coverage': 'percent_covered',
    }
    records = [  # noqa: ECE001
        {
            **{'File': f'`{Path(path_file).as_posix()}`'},
            **{col: file_obj['summary'][key] for col, key in col_key_map.items()},
        } for path_file, file_obj in coverage_data['files'].items()
    ]
    records.append({
        **{'File': '**Totals**'},
        **{col: coverage_data['totals'][key] for col, key in col_key_map.items()},
    })
    # Format table for Github Markdown
    df_cov = pd.DataFrame(records)
    df_cov['Coverage'] = df_cov['Coverage'].round(1).astype(str) + '%'
    lines_table = df_cov.to_markdown(index=False).split('\n')  # Note: requires optional "tabulate"
    lines_table.extend(['', f"Generated on: {coverage_data['meta']['timestamp']}"])
    return lines_table


@beartype
def _handle_coverage(line: str, _path_file: Path) -> List[str]:
    """Read the coverage.json file and write a Markdown table to the README file.

    Args:
        line: first line of the section
        path_file: path to the file that contained the string

    Returns:
        List[str]: list of auto-formatted text

    """
    path_coverage = DG.meta.path_project / 'coverage.json'  # Created by "task_coverage"
    lines_cov = []
    if path_coverage.is_file():
        coverage_data = json.loads(path_coverage.read_text())
        lines_cov = _format_cov_table(coverage_data)
    else:
        logger.warning(f'Could not locate: {path_coverage}')

    line_end = '<!-- {cte} -->'
    return [line] + lines_cov + [line_end]


@beartype
def write_autoformatted_md_sections() -> None:
    """Populate the auto-formatted sections of markdown files with user-configured logic.

    Raises:
        RuntimeError: if `DG.doc.handler_lookup` hasn't ben configured. See `_ensure_handler_lookup`

    """
    if DG.doc.handler_lookup is None:
        raise RuntimeError('The "DG.doc.handler_lookup" dictionary has not been created')

    logger.info('> {paths_md}', paths_md=DG.doc.paths_md)
    for path_md in DG.doc.paths_md:
        md_lines = _ReplacementMachine().parse(read_lines(path_md), DG.doc.handler_lookup, path_md)
        path_md.write_text('\n'.join(md_lines))


# ----------------------------------------------------------------------------------------------------------------------
# Working with Diagram


@beartype
def _diagram_tasks(pdoc_out_path: Path) -> List[DoitAction]:
    """Return actions to generate code diagrams in the module documentation directory.

    Note: must be run after `document` because pdocs will delete these files

    PUML support may be coming in a future release: https://github.com/PyCQA/pylint/issues/4498

    Args:
        pdoc_out_path: path to the top-level pdoc output. Expect subdir with module name

    Returns:
        List[DoitAction]: actions to generate the

    """
    diagram_md = """# Code Diagrams

> Auto-generated with `pylint-pyreverse`

## Packages

![./packages.svg](./packages.svg)

[Full Size](./packages.svg)

## Classes

![./classes.svg](./classes.svg)

[Full Size](./classes.svg)
"""
    path_diagram = pdoc_out_path / DG.meta.pkg_name / '_code_diagrams.md'
    return [
        (write_text, (path_diagram, diagram_md)),
        Interactive(f'poetry run pyreverse {DG.meta.pkg_name} --output svg --output-directory {path_diagram.parent}'),
    ]


# ----------------------------------------------------------------------------------------------------------------------
# Main Documentation Tasks


@beartype
def _ensure_handler_lookup() -> None:
    """Configure the handler lookup if not already configured."""
    if DG.doc.handler_lookup is None:
        DG.doc.handler_lookup = {
            'COVERAGE ': _handle_coverage,
            'SOURCE_FILE=': _handle_source_file,
        }


@beartype
def _find_and_trim_trailing_whitespace(doc_dir: Path) -> None:
    """Find all markdown files and trim any trailing whitespace."""
    for path_md in doc_dir.rglob('*/md'):
        trim_trailing_whitespace(path_md)


@beartype
def task_document() -> DoitTask:
    """Build the HTML documentation.

    Returns:
        DoitTask: doit task

    """
    _ensure_handler_lookup()
    pdoc_out_path = DG.doc.auto_doc_path
    pdoc_out = f'--output_dir {pdoc_out_path} --overwrite'
    pdoc_template = f'--template_dir {DG.calcipy_dir}/doit_tasks/templates'
    return debug_task([
        (write_autoformatted_md_sections, ()),
        (delete_dir, (pdoc_out_path,)),
        Interactive(f'poetry run pdocs as_markdown {DG.meta.pkg_name} {pdoc_out} {pdoc_template}'),
        *_diagram_tasks(pdoc_out_path),
        (_find_and_trim_trailing_whitespace, (pdoc_out_path,)),
        Interactive(f'poetry run mkdocs build --site-dir {DG.doc.path_out}'),
    ])


def _is_mkdocs_local() -> bool:
    """Check if mkdocs is configured for local output.

    See notes on local-link configuration here: https://github.com/timothycrosley/portray/issues/65

    Additional information on using local search here: https://github.com/wilhelmer/mkdocs-localsearch

    Returns:
        bool: True if configured for local file output rather than hosted

    """
    mkdocs_config = _read_yaml_file(DG.meta.path_project / _MKDOCS_CONFIG_NAME)
    return mkdocs_config.get('use_directory_urls') is False


@beartype
def task_open_docs() -> DoitTask:
    """Open the documentation files in the default browser.

    Returns:
        DoitTask: doit task

    """
    if _is_mkdocs_local():  # pragma: no cover
        path_doc_index = DG.doc.path_out / 'index.html'
        return debug_task([
            (open_in_browser, (path_doc_index,)),
        ])
    return debug_task([
        (webbrowser.open, ('http://localhost:8000',)),
        Interactive('poetry run mkdocs serve --dirtyreload'),
    ])


@beartype
def task_deploy_docs() -> DoitTask:
    """Deploy docs to the Github `gh-pages` branch.

    Returns:
        DoitTask: doit task

    """
    if _is_mkdocs_local():  # pragma: no cover
        return debug_task([
            (echo, ('ERROR: Not yet configured to deploy documentation without "use_directory_urls"',)),
        ])
    return debug_task([Interactive('poetry run mkdocs gh-deploy')])
