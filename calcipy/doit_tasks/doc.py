"""doit Documentation Utilities."""

import json
import re
import webbrowser
from pathlib import Path
from typing import Callable, Dict, List, Optional, Pattern

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
def _write_code_to_readme() -> None:
    """Replace commented sections in README with linked file contents."""
    comment_pattern = re.compile(r'\s*<!-- /?(CODE:.*) -->')
    fn = 'tests/examples/readme.py'
    script_path = DG.meta.path_project / fn
    if script_path.is_file():
        source_code = ['```py', *read_lines(script_path), '```']
        new_text = {f'CODE:{fn}': [f'{line}'.rstrip() for line in source_code]}
        {comment_pattern: new_text}
        # _write_to_readme(comment_pattern, new_text)
        # FIXME: implement this according to #36 changes
    else:
        logger.warning(f'Could not locate: {script_path}')


@beartype
def _write_coverage_to_readme() -> None:
    """Read the coverage.json file and write a Markdown table to the README file."""
    try:
        from subprocess_tee import run  # nosec # noqa: S404
    except ImportError:  # pragma: no cover
        from subprocess import run  # type: ignore[no-redef]  # nosec # noqa: S404
    # Attempt to create the coverage file
    run('poetry run python -m coverage json')  # nosec # noqa: S603, S607

    coverage_path = (DG.meta.path_project / 'coverage.json')
    if coverage_path.is_file():
        # Read coverage information from json file
        coverage = json.loads(coverage_path.read_text())
        # Collect raw data
        legend = ['File', 'Statements', 'Missing', 'Excluded', 'Coverage']
        int_keys = ['num_statements', 'missing_lines', 'excluded_lines']
        rows = [legend, ['--:'] * len(legend)]
        for path_file, file_obj in coverage['files'].items():
            rel_path = Path(path_file).resolve().relative_to(DG.meta.path_project).as_posix()
            per = round(file_obj['summary']['percent_covered'], 1)
            rows.append([f'`{rel_path}`'] + [file_obj['summary'][key] for key in int_keys] + [f'{per}%'])
        # Format table for Github Markdown
        table_lines = [f"| {' | '.join([str(value) for value in row])} |" for row in rows]
        table_lines.extend(['', f"Generated on: {coverage['meta']['timestamp']}"])
        # Replace coverage section in README
        # comment_pattern = re.compile(r'<!-- /?(COVERAGE) -->')
        # _write_to_readme(comment_pattern, {'COVERAGE': table_lines})
        # FIXME: implement this according to #36 changes


@beartype
def write_autoformatted_md_sections() -> None:
    """Populate the auto-formatted sections of markdown files with user-configured logic."""
    if DG.doc.handler_lookup is None:
        raise RuntimeError('The "DG.doc.handler_lookup" dictionary has not been created')

    logger.info('> {paths_md}', paths_md=DG.doc.paths_md)
    for path_md in DG.doc.paths_md:
        md_lines = _ReplacementMachine().parse(read_lines(path_md), DG.doc.handler_lookup, path_md)
        path_md.write_text('\n'.join(md_lines))


# ----------------------------------------------------------------------------------------------------------------------
# Main Documentation Tasks


@beartype
def _format_header(line: str, path_md: Path) -> str:
    """Replace the do not modify header information."""  # noqa: DAR101,DAR201,DAR401
    if '\n' in line:  # FIXME: Function signature has changed with the restored README Machine
        logger.error('Found: "{line}"', line=line)
        raise RuntimeError(f'Found unexpected newline in header comment of: {path_md}')
    return '<!-- Do not modify sections with "AUTO-*". They are updated by with a doit task -->'


@beartype
def _check_unknown(line: str, path_md: Path) -> str:
    """Pass-through to catch sections not parsed by the function logic."""  # noqa: DAR101,DAR201
    logger.warning('Could not parse: {line} from: {path_md}', line=line, path_md=path_md)
    return line


@beartype
def _configure_action_lookup() -> None:
    """Configure the action lookup for markdown file autoformatting if not already configured."""
    if DG.doc.handler_lookup is None:
        DG.doc.handler_lookup = {
            '<!-- Do not modify sections with ': _format_header,
            '<!-- ': _check_unknown,
        }


@beartype
def task_document() -> DoitTask:
    """Build the HTML documentation.

    Returns:
        DoitTask: doit task

    """
    _configure_action_lookup()
    return debug_task([
        (write_autoformatted_md_sections, ()),
        # PLANNED: Delete /docs/ folder
        # 'poetry run pdocs as_markdown calcipy --overwrite --template-dir? /path/dir',  # PLANNED: DG.package_name?
        # Copy all *.md (and */*.md?) files into /docs!
        # TODO: Remove all extra None ("\nNone\n") and "Module "...
        #   PLANNED: Consider a different template with different formatting for code and arguments?
        'poetry run mkdocs build',  # --site-dir DG.doc.path_out
    ])


# PLANNED: Only works for static documentation files (projects could use either mkdocs served or static...)
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
def task_serve_fast() -> DoitTask:
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
