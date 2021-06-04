"""doit Documentation Utilities."""

import json
import re
import webbrowser
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Pattern

from beartype import beartype
from doit.tools import Interactive
from loguru import logger
from transitions import Machine

from ..file_helpers import read_lines
from .base import debug_task, open_in_browser
from .doit_globals import DG, DoitTask

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
    path_cl.replace(DG.doc.doc_dir / path_cl.name)


@beartype
def task_cl_write() -> DoitTask:
    """Write a Changelog file with the raw Git history.

    Resources:

    - https://keepachangelog.com/en/1.0.0/
    - https://www.conventionalcommits.org/en/v1.0.0/
    - https://writingfordevelopers.substack.com/p/how-to-write-a-commit-message
    - https://chris.beams.io/posts/git-commit/
    - https://semver.org/
    - https://calver.org/

    Returns:
        DoitTask: doit task

    """
    return debug_task([
        'poetry run cz changelog',
        (_move_cl, ()),
    ])


@beartype
def task_cl_bump() -> DoitTask:
    """Bumps project version based on project history and settings in pyproject.toml.

    Returns:
        DoitTask: doit task

    """
    return debug_task([
        Interactive('poetry run cz bump --changelog --annotated-tag'),
        (_move_cl, ()),
        'git push origin --tags --no-verify',
    ])


@beartype
def task_cl_bump_pre() -> DoitTask:
    """Bump with specified pre-release tag. Creates Changelog.

    Example: `doit run cl_bump_pre -p alpha` or `doit run cl_bump_pre -p rc`

    Returns:
        DoitTask: doit task

    """
    task = debug_task([
        Interactive('poetry run cz bump --changelog --prerelease %(prerelease)s'),
        (_move_cl, ()),
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
        super().__init__(states=[self.state_user, self.state_auto],
                         initial=self.state_user,
                         transitions=transitions)

    def parse(self, lines: List[str], handler_lookup: Dict[str, Callable[[str, Path], str]],  # noqa: CCR001
              path_file: Optional[Path] = None) -> List[str]:
        """Parse lines and insert new_text based on provided handler_lookup.

        Args:
            lines: list of string from source file
            handler_lookup: Lookup dictionary for autoformatted sections
            path_file: optional path to the file. Only useful for debugging

        Returns:
            List[str]: modified list of strings

        """
        lines_new = []
        for line in lines:
            if '{cte}' in line and self.state == self.state_auto:  # end
                self.end()
            elif '{cts}' in line:  # start
                self.start_auto()
                for text_match, handler in handler_lookup.items():
                    if text_match in line:
                        lines_new.extend(handler(line, path_file))
                        break
                else:
                    logger.error('Could not parse: {line}', line=line)
                    lines_new.append(line)
                    self.end()
            elif self.state == self.state_user:
                lines_new.append(line)
            # else: discard the lines in the auto-section

        return lines_new


_RE_VAR_COMMENT_HTML = re.compile(r'<!-- {cts} (?P<key>[^=]+)=(?P<value>[^;]+);')
"""Regex for extracting the vairable from an HTML code comment."""


@beartype
def _parse_var_comment(section: str, matcher: Pattern = _RE_VAR_COMMENT_HTML) -> Dict[str, str]:
    """Parse the variable from a matching comment.

    Examples:
    - `<!-- rating=1; (User can specify rating on scale of 1-5) -->`
    - `<!-- path_image=./docs/imgs/image_filename.png; -->`
    - `<!-- tricky_var_3=-11e-21; -->`

    Args:
        section: string from source file
        matcher: regex pattern to match. Default is `_RE_VAR_COMMENT_HTML`

    Returns:
        Dict[str, str]: single key and value pair based on the parsed comment

    Raises:
        AttributeError: if the section couldn't be parsed with the specified regular expression

    """
    try:
        match = matcher.match(section.strip())
        if match:
            matches = match.groupdict()
            return {matches['key']: matches['value']}
        return {}
    except AttributeError:
        logger.exception('Error parsing `{section}` with `{matcher}`', section=section, matcher=matcher)
        raise


@beartype
def _handle_source_file(line: str, path_file: Path) -> List[str]:
    """Replace commented sections in README with linked file contents.

    Args:
        line: first line of the section
        path_file: path to the file that contained the string

    Returns:
        List[str]: list of auto-formatted text

    """
    path_rel = _parse_var_comment(line)['SOURCE_FILE']
    path_base = DG.meta.path_project if path_rel.startswith('/') else path_file.resolve().parent
    path_source = path_base / path_rel.lstrip('/')
    language = path_source.suffix.lstrip('.')
    lines_source = [f'```{language}', *read_lines(path_source), '```']
    if not path_source.is_file():
        logger.warning(f'Could not locate: {path_source}')

    line_start = f'<!-- {{cts}} SOURCE_FILE={path_rel}; -->'
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
    legend = ['File', 'Statements', 'Missing', 'Excluded', 'Coverage']
    int_keys = ['num_statements', 'missing_lines', 'excluded_lines']
    rows = [legend, ['--:'] * len(legend)]
    for path_file, file_obj in coverage_data['files'].items():
        rel_path = Path(path_file).as_posix()  # .resolve().relative_to(DG.meta.path_project)
        per = round(file_obj['summary']['percent_covered'], 1)
        rows.append([f'`{rel_path}`'] + [file_obj['summary'][key] for key in int_keys] + [f'{per}%'])
    # Format table for Github Markdown
    lines_table = [f"| {' | '.join([str(value) for value in row])} |" for row in rows]
    lines_table.extend(['', f"Generated on: {coverage_data['meta']['timestamp']}"])
    # TODO: Convert to Pandas for ".to_markdown"
    #   https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_markdown.html
    # TODO: Add summary line for total coverage statistics
    return lines_table


@beartype
def _handle_coverage(line: str, path_file: Path) -> List[str]:
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

    line_start = '<!-- {cts} COVERAGE -->'
    line_end = '<!-- {cte} -->'
    return [line_start] + lines_cov + [line_end]


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
# Main Documentation Tasks


@beartype
def _ensure_handler_lookup() -> None:
    """Configure the handler lookup if not already configured."""
    if DG.doc.handler_lookup is None:
        DG.doc.handler_lookup = {
            'COVERAGE': _handle_coverage,
            'SOURCE_FILE=': _handle_source_file,
        }


@beartype
def task_document() -> DoitTask:
    """Build the HTML documentation.

    Returns:
        DoitTask: doit task

    """
    _ensure_handler_lookup()
    return debug_task([
        (write_autoformatted_md_sections, ()),

        # FIXME: Next steps to implement the code documentation. Try pdoc and compare against pdocs

        # 'poetry run pdocs as_markdown calcipy --overwrite --template-dir? /path/dir',  # PLANNED: DG.package_name?
        # Copy all *.md (and */*.md?) files into /docs!
        # TODO: Remove all extra None ("\nNone\n") and "Module "...
        #   PLANNED: Consider a different template with different formatting for code and arguments?
        'poetry run mkdocs build',  # --site-dir DG.doc.path_out
    ])


# TODO: Only works for static documentation files (projects could use either mkdocs served or static...)
@beartype
def task_open_docs() -> DoitTask:
    """Open the documentation files in the default browser.

    Returns:
        DoitTask: doit task

    """
    path_doc_index = DG.doc.path_out / DG.meta.pkg_name / 'index.html'
    return debug_task([
        (open_in_browser, (path_doc_index,)),
    ])


@beartype
def task_serve_docs() -> DoitTask:
    """Serve the site with `--dirtyreload` and open in a web browser.

    Note: use only for large projects. `poetry run mkdocs serve` is preferred for smaller projects

    Returns:
        DoitTask: doit task

    """
    return debug_task([
        (webbrowser.open, ('http://localhost:8000',)),
        Interactive('poetry run mkdocs serve --dirtyreload'),
    ])


@beartype
def task_deploy() -> DoitTask:
    """Deploy to Github `gh-pages` branch.

    Returns:
        DoitTask: doit task

    """
    return debug_task([Interactive('poetry run mkdocs gh-deploy')])
