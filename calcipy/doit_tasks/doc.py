"""doit Documentation Utilities."""

import json
import re
import webbrowser
from pathlib import Path
from typing import Callable, Dict, List

from doit.tools import Interactive
from loguru import logger
from transitions import Machine

from .base import debug_task, open_in_browser, read_lines
from .doit_globals import DG, DoitTask

# ----------------------------------------------------------------------------------------------------------------------
# Manage Changelog


def _move_cl() -> None:
    """Move the `CHANGELOG.md` file to the document directory.

    Raises:
        FileNotFoundError: if the changelog was not found

    """
    path_cl = DG.meta.path_project / 'CHANGELOG.md'
    if not path_cl.is_file():
        raise FileNotFoundError(f'Could not locate the changelog at: {path_cl}')
    path_cl.replace(DG.doc.doc_dir / path_cl.name)


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


class _MarkdownMachine(Machine):  # noqa: H601
    """State machine to replace auto-formatted comment sections of markdown files with handler callback."""

    states: List[str] = ['user', 'autoformatted']

    transitions: List[Dict[str, str]] = [
        {'trigger': 'start_auto', 'source': 'user', 'dest': 'autoformatted'},
        {'trigger': 'end', 'source': 'autoformatted', 'dest': 'user'},
    ]

    def __init__(self) -> None:
        """Initialize the state machine."""
        super().__init__(states=self.states, initial=self.states[0], transitions=self.transitions)

    def parse(  # noqa: CCR001
        self, lines: List[str], handlers: Dict[str, Callable[[str, Path], str]],
    ) -> List[str]:
        """Parse lines and insert new_text based on provided handlers.

        Args:
            lines: list of string from source file
            handlers: Lookup dictionary for autoformatted sections of the project's markdown files

        Returns:
            List[str]: modified list of strings

        """
        lines_modified = []
        for line in lines:
            line_strip = line.strip()
            if line_strip.endswith(' // -->'):
                lines_modified.append(line)
                self.end()
            elif line_strip.startswith('<--?'):
                self.start_auto()
                for startswith, handler in handlers.items():
                    if line_strip.startswith(startswith):
                        path_md = Path.home()  # FIXME: Need to handle passing the path for debugging
                        lines_modified.extend(handler(line, path_md))
                        break
                else:
                    logger.error(f'Could not parse comment: {line}', line=line)
            elif self.state == 'user':
                lines_modified.append(line)

        return lines_modified


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


def _write_coverage_to_readme() -> None:
    """Read the coverage.json file and write a Markdown table to the README file."""
    try:
        from subprocess_tee import run  # noqa: S404
    except ImportError:  # pragma: no cover
        from subprocess import run  # type: ignore  # noqa: S404
    # Attempt to create the coverage file
    run('poetry run python -m coverage json')  # noqa: S603, S607

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


def write_autoformatted_md_sections() -> None:
    """Populate the auto-formatted sections of markdown files with user-configured logic."""
    logger.info('> {paths_md}', paths_md=DG.doc.paths_md)
    for path_md in DG.doc.paths_md:
        md_lines = _MarkdownMachine().parse(read_lines(path_md), DG.doc.startswith_action_lookup)
        path_md.write_text('\n'.join(md_lines))


# ----------------------------------------------------------------------------------------------------------------------
# mkdocs


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


def task_deploy() -> DoitTask:
    """Deploy to Github `gh-pages` branch.

    Returns:
        DoitTask: doit task

    """
    return debug_task([Interactive('poetry run mkdocs gh-deploy')])


# ----------------------------------------------------------------------------------------------------------------------
# Main Documentation Tasks


def _format_header(line: str, path_md: Path) -> str:
    """Replace the do not modify header information."""  # noqa: DAR101,DAR201,DAR401
    if '\n' in line:  # FIXME: Function signature has changed with the restored README Machine
        logger.error('Found: "{line}"', line=line)
        raise RuntimeError(f'Found unexpected newline in header comment of: {path_md}')
    return '<!-- Do not modify sections with "AUTO-*". They are updated by with a doit task -->'


def _check_unknown(line: str, path_md: Path) -> str:
    """Pass-through to catch sections not parsed by the function logic."""  # noqa: DAR101,DAR201
    logger.warning('Could not parse: {line} from: {path_md}', line=line, path_md=path_md)
    return line


def _configure_action_lookup() -> None:
    """Configure the action lookup for markdown file autoformatting if not already configured."""
    if not [*DG.doc.startswith_action_lookup.keys()]:
        DG.doc.startswith_action_lookup = {
            '<!-- Do not modify sections with ': _format_header,
            '<!-- ': _check_unknown,
        }


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
def task_open_docs() -> DoitTask:
    """Open the documentation files in the default browser.

    Returns:
        DoitTask: doit task

    """
    path_doc_index = DG.doc.path_out / DG.meta.pkg_name / 'index.html'
    return debug_task([
        (open_in_browser, (path_doc_index,)),
    ])
