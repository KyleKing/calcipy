"""Markup Machine."""

from __future__ import annotations

import json
import re
import shlex
import subprocess  # noqa: S404
from pathlib import Path

from beartype.typing import Any, Callable, Dict, List, Optional
from corallium.file_helpers import read_lines
from corallium.file_search import find_project_files_by_suffix
from corallium.log import LOGGER
from corallium.markup_table import format_table

from calcipy.invoke_helpers import get_project_path

HandlerLookupT = Dict[str, Callable[[str, Path], List[str]]]
"""Handler Lookup."""


class _ParseSkipError(RuntimeError):
    """Exception caught if the handler does not want to replace the text."""


class _ReplacementMachine:
    """State machine to replace content with user-specified handlers.

    Uses `[cts]`/`{cts}` and `[cte]`/`{cte}` to demarcate sections (calcipy-template-start/end).

    """

    def __init__(self) -> None:
        """Initialize the state machine."""
        self.in_template = False

    def parse(
        self,
        lines: List[str],
        handler_lookup: HandlerLookupT,
        path_file: Path,
    ) -> List[str]:
        """Parse lines and insert new_text based on provided handler_lookup.

        Args:
            lines: list of string from source file
            handler_lookup: Lookup dictionary for template-formatted sections
            path_file: optional path to the file. Only useful for debugging

        Returns:
            List[str]: modified list of strings

        """
        updated_lines = []
        for line in lines:
            updated_lines.extend(self._parse_line(line, handler_lookup, path_file))
        return updated_lines

    def _parse_line(
        self,
        line: str,
        handler_lookup: HandlerLookupT,
        path_file: Path,
    ) -> List[str]:
        """Parse lines and insert new_text based on provided handler_lookup.

        Args:
            line: single line
            handler_lookup: lookup dictionary for template-formatted sections
            path_file: optional path to the file. Only useful for debugging

        Returns:
            List[str]: modified list of strings

        """
        lines: List[str] = []
        if _has_marker(line, 'end') and self.in_template:
            self.in_template = False
        elif _has_marker(line, 'start'):
            self.in_template = True
            matches = [text_match for text_match in handler_lookup if text_match in line]
            if len(matches) == 1:
                [match] = matches
                try:
                    lines.extend(handler_lookup[match](line, path_file))
                except _ParseSkipError:
                    lines.append(line)
                    self.in_template = False
            else:
                LOGGER.debug('Could not parse. Skipping:', line=line)
                lines.append(line)
                self.in_template = False
        elif not self.in_template:
            lines.append(line)
        # else: discard the lines in the template-section
        return lines


_COMMENT_VARS = re.compile(r'[<!\-{%]+ [{\[]cts[}\]] (?P<key>[^=]+)=(?P<value>[^;]+);')
"""Regex for extracting the variable from a markup comment."""


def _has_marker(line: str, marker_type: str) -> bool:
    """Check if line contains a marker.

    Args:
        line: line to check
        marker_type: 'start' for cts markers, 'end' for cte markers

    Returns:
        True if line contains the marker

    """
    marker = 'cts' if marker_type == 'start' else 'cte'
    return f'[{marker}]' in line or f'{{{marker}}}' in line


def _parse_var_comment(line: str) -> Dict[str, str]:
    """Parse the variable from a matching comment.

    Args:
        line: string from source file

    Returns:
        Dict[str, str]: single key and value pair based on the parsed comment

    """
    if match := _COMMENT_VARS.match(line.strip()):
        groups = match.groupdict()
        return {groups['key']: groups['value']}
    return {}


def _is_html_comment(line: str) -> bool:
    """Check if line uses HTML comment style."""
    return line.strip().startswith('<!--')


def _format_start_marker(line: str, key: str, value: str) -> str:
    """Format a start marker preserving the comment style from input."""
    if _is_html_comment(line):
        return f'<!-- {{cts}} {key}={value}; -->'
    return f'{{% [cts] {key}={value}; %}}'


def _format_end_marker(line: str) -> str:
    """Format an end marker preserving the comment style from input."""
    if _is_html_comment(line):
        return '<!-- {cte} -->'
    return '{% [cte] %}'


def _handle_source_file(line: str, path_file: Path) -> List[str]:
    """Replace commented sections in README with linked file contents.

    Args:
        line: first line of the section
        path_file: path to the file that contained the string

    Returns:
        List[str]: list of template-formatted text

    """
    key, path_rel = next(iter(_parse_var_comment(line).items()))
    path_base = get_project_path() if path_rel.startswith('/') else path_file.resolve().parent
    path_source = path_base / path_rel.lstrip('/')
    language = path_source.suffix.lstrip('.')
    lines_source = [f'```{language}', *read_lines(path_source), '```']
    if not path_source.is_file():  # pragma: no cover
        LOGGER.warning('Could not locate source file', path_source=path_source)

    return [_format_start_marker(line, key, path_rel), *lines_source, _format_end_marker(line)]


def _format_cov_table(coverage_data: Dict[str, Any]) -> List[str]:
    """Format code coverage data table.

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
    records = [
        {
            'File': f'`{Path(path_file).as_posix()}`',
            **{col: file_obj['summary'][key] for col, key in col_key_map.items()},
        }
        for path_file, file_obj in coverage_data['files'].items()
    ]
    records.append(
        {
            'File': '**Totals**',
            **{col: coverage_data['totals'][key] for col, key in col_key_map.items()},
        },
    )
    records = [{**r_, 'Coverage': f'{round(float(r_["Coverage"]), 1)}%'} for r_ in records]

    delimiters = ['-', *(['-:'] * len(col_key_map))]
    lines_table = format_table(headers=['File', *col_key_map], records=records, delimiters=delimiters).split('\n')
    short_date = coverage_data['meta']['timestamp'].split('T')[0]
    lines_table.extend(['', f'Generated on: {short_date}'])
    return lines_table


def _handle_coverage(line: str, _path_file: Path, path_coverage: Optional[Path] = None) -> List[str]:
    """Read the coverage.json file and write a table to the README file.

    Args:
        line: first line of the section
        _path_file: path to the file that contained the string (unused)
        path_coverage: full path to a coverage.json file or defaults to the project

    Returns:
        List[str]: list of template-formatted text

    Raises:
        _ParseSkipError: if the "coverage.json" file is not available

    """
    path_coverage = path_coverage or get_project_path() / 'coverage.json'
    if not path_coverage.is_file():
        msg = f'Could not locate: {path_coverage}'
        raise _ParseSkipError(msg)
    coverage_data = json.loads(path_coverage.read_text())
    lines_cov = _format_cov_table(coverage_data)
    return [line, *lines_cov, _format_end_marker(line)]


_CLI_ALLOWED_PREFIXES = ('./run', 'uv ', 'python -m ', 'python3 -m ')


def _handle_cli_output(line: str, _path_file: Path) -> List[str]:
    """Execute CLI command and insert output into markdown.

    Args:
        line: marker line containing command
        _path_file: path to the markdown file (unused)

    Returns:
        List of lines with command output wrapped in code fence

    Raises:
        _ParseSkipError: if command is not allowed or execution fails

    """
    vars_parsed = _parse_var_comment(line)
    command = vars_parsed.get('CLI_OUTPUT', '')

    if not command or not any(command.startswith(prefix) for prefix in _CLI_ALLOWED_PREFIXES):
        msg = f'Command not allowed. Must start with one of: {_CLI_ALLOWED_PREFIXES}'
        raise _ParseSkipError(msg)

    try:
        result = subprocess.run(  # noqa: S603
            shlex.split(command),
            capture_output=True,
            text=True,
            cwd=get_project_path(),
            timeout=30,
            check=False,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as err:  # pragma: no cover
        LOGGER.warning('CLI command failed', command=command, error=str(err))
        raise _ParseSkipError(str(err)) from err

    output = result.stdout or result.stderr
    if result.returncode != 0 and not output:  # pragma: no cover
        msg = f'Command failed with exit code {result.returncode}'
        LOGGER.warning(msg, command=command)
        raise _ParseSkipError(msg)

    lines_output = ['```txt', *output.rstrip().split('\n'), '```']
    return [_format_start_marker(line, 'CLI_OUTPUT', command), *lines_output, _format_end_marker(line)]


def write_template_formatted_sections(
    handler_lookup: Optional[HandlerLookupT] = None,
    paths: Optional[List[Path]] = None,
) -> None:
    """Populate the template-formatted sections of markup files with user-configured logic."""
    lookup: HandlerLookupT = handler_lookup or {
        'CLI_OUTPUT=': _handle_cli_output,
        'COVERAGE ': _handle_coverage,
        'SOURCE_FILE=': _handle_source_file,
    }

    markup_paths = paths or find_project_files_by_suffix(get_project_path()).get('md') or []
    for path in markup_paths:
        LOGGER.text_debug('Processing', path=path)
        if lines := _ReplacementMachine().parse(read_lines(path), lookup, path):
            path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
