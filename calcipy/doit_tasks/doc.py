"""doit Documentation Utilities."""

import json
import re
import webbrowser
from pathlib import Path
from typing import Dict, List, Optional, Pattern

from doit.tools import InteractiveAction, LongRunning
from loguru import logger

from .base import debug_task, echo, open_in_browser, read_lines
from .doit_globals import DIG, DoItTask

try:
    from transitions import Machine
except ImportError:
    Machine = None

# ----------------------------------------------------------------------------------------------------------------------
# Manage Changelog


def task_cl_write() -> DoItTask:
    """Write a Changelog file with the raw Git history.

    Resources:

    - https://keepachangelog.com/en/1.0.0/
    - https://www.conventionalcommits.org/en/v1.0.0/
    - https://writingfordevelopers.substack.com/p/how-to-write-a-commit-message
    - https://chris.beams.io/posts/git-commit/
    - https://semver.org/
    - https://calver.org/

    Returns:
        DoItTask: doit task

    """
    return debug_task(['poetry run cz changelog'])


def task_cl_bump() -> DoItTask:
    """Bumps project version based on project history and settings in pyproject.toml.

    Returns:
        DoItTask: doit task

    """
    return debug_task([
        InteractiveAction('poetry run cz bump --changelog --annotated-tag'),
        (echo, ('Attempting to push tags to origin with pre-commit checks',)),
        'git push origin --tags',
    ])


def task_cl_bump_pre() -> DoItTask:
    """Bump with specified pre-release tag. Creates Changelog.

    Example: `doit run cl_bump_pre -p alpha` or `doit run cl_bump_pre -p rc`

    Returns:
        DoItTask: doit task

    """
    task = debug_task([
        InteractiveAction('poetry run cz bump --changelog --prerelease %(prerelease)s'),
        'git push origin --tags --no-verify',
    ])
    task['params'] = [{
        'name': 'prerelease', 'short': 'p', 'long': 'prerelease', 'default': '',
        'help': 'Specify prerelease version for bump (alpha, beta, rc)',
    }]
    return task


# ----------------------------------------------------------------------------------------------------------------------
# Manage README Updates


class _ReadMeMachine:  # noqa: H601
    """State machine to replace commented sections of readme with new text."""

    states: List[str] = ['readme', 'new']

    transitions: List[Dict[str, str]] = [
        {'trigger': 'start_new', 'source': 'readme', 'dest': 'new'},
        {'trigger': 'end', 'source': 'new', 'dest': 'readme'},
    ]

    readme_lines: Optional[List[str]] = None

    def __init__(self) -> None:
        """Initialize state machine."""
        self.machine = Machine(model=self, states=self.states, initial='readme', transitions=self.transitions)

    def parse(  # noqa: CCR001
        self, lines: List[str], comment_pattern: Pattern[str],
        new_text: Dict[str, str],
    ) -> List[str]:
        """Parse lines and insert new_text.

        Args:
            lines: list of text files
            comment_pattern: comment pattern to match (ex: ``)
            new_text: dictionary with comment string as key

        Returns:
            list: list of strings for README

        """
        self.readme_lines = []
        for line in lines:
            if comment_pattern.match(line):
                self.readme_lines.append(line)
                if line.strip().startswith('<!-- /'):
                    self.end()
                else:
                    key = comment_pattern.match(line).group(1)
                    self.readme_lines.extend(['', *new_text[key], ''])
                    self.start_new()
            elif self.state == 'readme':
                self.readme_lines.append(line)

            new_line = self.readme_lines[-1]
            made_change = (line != new_line)
            logger.debug(
                'Parsed README Line', self_state=self.state, line=line,
                made_change=made_change, new_line=new_line if made_change else None,
            )

        return self.readme_lines


# FIXME: This was for a very specific implementation. See #36 for variable defintion
def _write_to_readme(comment_pattern: Pattern[str], new_text: Dict[str, str]) -> None:
    """Wrap _ReadMeMachine. Handle reading then writing changes to the README.

    Args:
        comment_pattern: comment pattern to match (ex: ``)
        new_text: dictionary with comment string as key

    """
    readme_path = DIG.meta.path_project / 'README.md'
    readme_lines = _ReadMeMachine().parse(read_lines(readme_path), comment_pattern, new_text)
    readme_path.write_text('\n'.join(readme_lines))


def _write_code_to_readme() -> None:
    """Replace commented sections in README with linked file contents."""
    comment_pattern = re.compile(r'\s*<!-- /?(CODE:.*) -->')
    fn = 'tests/examples/readme.py'
    script_path = DIG.meta.path_project / fn
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
    except ImportError:
        from subprocess import run  # noqa: S404
    # Attempt to create the coverage file
    run('poetry run python -m coverage json')  # noqa: S603, S607

    coverage_path = (DIG.meta.path_project / 'coverage.json')
    if coverage_path.is_file():
        # Read coverage information from json file
        coverage = json.loads(coverage_path.read_text())
        # Collect raw data
        legend = ['File', 'Statements', 'Missing', 'Excluded', 'Coverage']
        int_keys = ['num_statements', 'missing_lines', 'excluded_lines']
        rows = [legend, ['--:'] * len(legend)]
        for file_path, file_obj in coverage['files'].items():
            rel_path = Path(file_path).resolve().relative_to(DIG.meta.path_project).as_posix()
            per = round(file_obj['summary']['percent_covered'], 1)
            rows.append([f'`{rel_path}`'] + [file_obj['summary'][key] for key in int_keys] + [f'{per}%'])
        # Format table for Github Markdown
        table_lines = [f"| {' | '.join([str(value) for value in row])} |" for row in rows]
        table_lines.extend(['', f"Generated on: {coverage['meta']['timestamp']}"])
        # Replace coverage section in README
        # comment_pattern = re.compile(r'<!-- /?(COVERAGE) -->')
        # _write_to_readme(comment_pattern, {'COVERAGE': table_lines})
        # FIXME: implement this according to #36 changes


# ----------------------------------------------------------------------------------------------------------------------
# Markdown Formatting
# PLANNED: Integrate with/replace the above ReadMeMachine (#36)


def _autoformat_md(path_md: Path) -> str:
    """Autoformat the sections of the specified markdown file.

    Args:
        path_md: Path to the markdown file

    Returns:
        str: updated markdown file with autoformatted sections replaced with new content

    """
    sections = []
    for section in path_md.read_text().split('\n\n'):
        for startswith, action in DIG.doc.startswith_action_lookup.items():
            if section.strip().startswith(startswith):
                sections.append(action(section, path_md))
                break
        else:
            sections.append(section)
    return '\n\n'.join(sections)


def write_autoformatted_md_sections() -> None:
    """Populate the auto-formatted sections of markdown files with user-configured logic."""
    for path_md in DIG.doc.paths_md:
        logger.info('> {path_md}', path_md=path_md)
        path_md.write_text(_autoformat_md(path_md))


# ----------------------------------------------------------------------------------------------------------------------
# mkdocs


def task_serve_fast() -> DoItTask:
    """Serve the site with `--dirtyreload` and open in a web browser.

    Note: use only for large projects. `poetry run mkdocs serve` is preferred for smaller projects

    Returns:
        DoItTask: doit task

    """
    return debug_task([
        (webbrowser.open, ('http://localhost:8000',)),
        LongRunning('poetry run mkdocs serve --dirtyreload'),
    ])


def task_deploy() -> DoItTask:
    """Deploy to Github `gh-pages` branch.

    Returns:
        DoItTask: doit task

    """
    return debug_task([LongRunning('poetry run mkdocs gh-deploy')])


# ----------------------------------------------------------------------------------------------------------------------
# Main Documentation Tasks


def _format_header(section: str, path_md: Path) -> str:
    """Replace the do not modify header information."""  # noqa: DAR101,DAR201,DAR401
    if '\n' in section:
        logger.error('Found: "{section}"', section=section)
        raise RuntimeError(f'Found unexpected newline in header comment of: {path_md}')
    return '<!-- Do not modify sections with "AUTO-*". They are updated by with a DoIt task -->'


def _check_unknown(section: str, path_md: Path) -> str:
    """Pass-through to catch sections not parsed by the function logic."""  # noqa: DAR101,DAR201
    logger.warning('Could not parse: {section} from: {path_md}', section=section, path_md=path_md)
    return section


def _configure_action_lookup() -> None:
    """Configure the action lookup for markdown file autoformatting if not already configured."""
    if DIG.doc.startswith_action_lookup is None:
        DIG.doc.startswith_action_lookup = {
            '<!-- Do not modify sections with ': _format_header,
            '<!-- ': _check_unknown,
        }


def task_document() -> DoItTask:
    """Build the HTML documentation.

    Returns:
        DoItTask: doit task

    """
    _configure_action_lookup()
    return debug_task([
        (write_autoformatted_md_sections, ()),
        # PLANNED: Delete /docs/ folder
        # 'poetry run pdocs as_markdown calcipy --overwrite --template-dir? /path/dir',  # PLANNED: DIG.package_name?
        # Copy all *.md (and */*.md?) files into /docs!
        # TODO: Remove all extra None ("\nNone\n") and "Module "...
        #   PLANNED: Consider a different template with different formatting for code and arguments?
        'poetry run mkdocs build',  # --site-dir DIG.doc.path_out
    ])


# PLANNED: Only works for static documentation files (projects could use either mkdocs served or static...)
def task_open_docs() -> DoItTask:
    """Open the documentation files in the default browser.

    Returns:
        DoItTask: doit task

    """
    path_doc_index = DIG.doc.path_out / DIG.meta.pkg_name / 'index.html'
    return debug_task([
        (open_in_browser, (path_doc_index,)),
    ])
